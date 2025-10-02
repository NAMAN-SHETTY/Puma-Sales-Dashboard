import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html

# ---------------- Load Data ----------------
df = pd.read_csv("Puma_Dataset.csv")
df["Invoice Date"] = pd.to_datetime(df["Invoice Date"], format="%d-%m-%Y", errors="coerce")
df["Total Sales"] = pd.to_numeric(df["Total Sales"], errors="coerce")  # <-- Add this line
# Convert numbers safely
df["Price per Unit"] = pd.to_numeric(
    df["Price per Unit"].astype(str).str.replace(r"[^\d.]", "", regex=True),
    errors="coerce"
)
df["Units Sold"] = pd.to_numeric(
    df["Units Sold"].astype(str).str.replace(r"[^\d.]", "", regex=True),
    errors="coerce"
)

# Drop rows where values are missing
df = df.dropna(subset=["Price per Unit", "Units Sold"])

# ---------------- KPI Calculations ----------------
df["Total Sales"] = df["Price per Unit"] * df["Units Sold"]
print("Total Sales Sum:", df["Total Sales"].sum())
top_region = df.groupby("Region")["Total Sales"].sum().idxmax()
top_retailer = df.groupby("Retailer")["Total Sales"].sum().idxmax()
# Ensure Invoice Date is datetime
df["Invoice Date"] = pd.to_datetime(df["Invoice Date"], errors="coerce", dayfirst=True)

# Group by year
yearly_sales = df.groupby(df["Invoice Date"].dt.year)["Total Sales"].sum().reset_index()
print(yearly_sales)

# Calculate YoY growth
if len(yearly_sales) > 1:
    yoy_growth = round(
        ((yearly_sales["Total Sales"].iloc[-1] - yearly_sales["Total Sales"].iloc[0]) 
        / yearly_sales["Total Sales"].iloc[0]) * 100, 2
    )
else:
    yoy_growth = 0

print("YoY Growth:", yoy_growth)

# ---------------- Charts ----------------
# Sales by Region & State
sales_region_state = df.groupby(["Region", "State"])["Total Sales"].sum().reset_index()
fig_sales_perf = px.bar(
    sales_region_state, x="Total Sales", y="State", color="Region",
    orientation="h", title="Total Sales by Region and State",
    color_discrete_sequence=["#FF0000", "#990000", "#FF5555", "#CC0000"]
)
fig_sales_perf.update_layout(
    paper_bgcolor="#111111", plot_bgcolor="#111111",
    font=dict(color="white"), title_font=dict(size=18, color="white", family="Arial")
)

# Profitability Metrics (Sales Method)
sales_method = df.groupby("Sales Method")["Total Sales"].sum().reset_index()
fig_profitability = px.pie(
    sales_method, names="Sales Method", values="Total Sales",
    hole=0.4, title="Profitability Metrics",
    color_discrete_sequence=["#FF0000", "#AA0000"]
)
fig_profitability.update_layout(
    paper_bgcolor="#111111", font=dict(color="white"), title_font=dict(size=18, color="white")
)

# Operating Margin Distribution
fig_margin = px.histogram(df, x="Operating Margin", nbins=20, title="Operating Margin Distribution",
                          color_discrete_sequence=["#FF0000"])
fig_margin.update_layout(
    paper_bgcolor="#111111", plot_bgcolor="#111111",
    font=dict(color="white"), title_font=dict(size=18, color="white")
)

# Monthly Sales Trend
monthly_sales = df.groupby(df["Invoice Date"].dt.to_period("M"))["Total Sales"].sum().reset_index()
monthly_sales["Invoice Date"] = monthly_sales["Invoice Date"].astype(str)
fig_trend = px.line(
    monthly_sales, x="Invoice Date", y="Total Sales", title="Monthly Sales Trend",
    markers=True
)
fig_trend.update_traces(line=dict(color="#FF0000", width=3), marker=dict(size=8, color="white"))
fig_trend.update_layout(
    paper_bgcolor="#111111", plot_bgcolor="#111111",
    font=dict(color="white"), title_font=dict(size=18, color="white")
)

# Units Sold per Product
product_sales = df.groupby("Product")["Units Sold"].sum().reset_index()
fig_product = px.bar(
    product_sales, x="Units Sold", y="Product", orientation="h",
    title="Units Sold per Product Category", color_discrete_sequence=["#FF0000"]
)
fig_product.update_layout(
    paper_bgcolor="#111111", plot_bgcolor="#111111",
    font=dict(color="white"), title_font=dict(size=18, color="white")
)

# ---------------- Dash App Layout ----------------
app = Dash(__name__)

app.layout = html.Div(style={"backgroundColor": "#111111", "color": "white", "padding": "20px"}, children=[

    html.H1("Puma Sales Dashboard", style={
        "textAlign": "center", "color": "#FF0000", "fontWeight": "bold", "fontFamily": "Arial"
    }),

    # KPI Cards
    html.Div([
        html.Div([
            html.H3("💰 Total Sales", style={"color": "#FF0000"}),
            html.P(f"${df['Total Sales'].sum():,.0f}", style={"fontSize": "22px", "fontWeight": "bold"})
        ], style={"width": "23%", "display": "inline-block", "textAlign": "center",
                  "backgroundColor": "#222222", "padding": "15px", "margin": "5px", "borderRadius": "10px"}),

        html.Div([
            html.H3("🌍 Top Region", style={"color": "#FF0000"}),
            html.P(top_region, style={"fontSize": "22px", "fontWeight": "bold"})
        ], style={"width": "23%", "display": "inline-block", "textAlign": "center",
                  "backgroundColor": "#222222", "padding": "15px", "margin": "5px", "borderRadius": "10px"}),

        html.Div([
            html.H3("🏪 Top Retailer", style={"color": "#FF0000"}),
            html.P(top_retailer, style={"fontSize": "22px", "fontWeight": "bold"})
        ], style={"width": "23%", "display": "inline-block", "textAlign": "center",
                  "backgroundColor": "#222222", "padding": "15px", "margin": "5px", "borderRadius": "10px"}),

        html.Div([
            html.H3("📈 YoY Growth", style={"color": "#FF0000"}),
            html.P(f"{yoy_growth}%", style={"fontSize": "22px", "fontWeight": "bold"})
        ], style={"width": "23%", "display": "inline-block", "textAlign": "center",
                  "backgroundColor": "#222222", "padding": "15px", "margin": "5px", "borderRadius": "10px"}),
    ], style={"display": "flex", "justifyContent": "space-around"}),

    # First row of charts
    html.Div([
        dcc.Graph(figure=fig_sales_perf, style={"width": "48%", "display": "inline-block"}),
        dcc.Graph(figure=fig_profitability, style={"width": "48%", "display": "inline-block"})
    ]),

    # Second row
    html.Div([
        dcc.Graph(figure=fig_margin, style={"width": "48%", "display": "inline-block"}),
        dcc.Graph(figure=fig_trend, style={"width": "48%", "display": "inline-block"})
    ]),

    # Third row
    html.Div([
        dcc.Graph(figure=fig_product, style={"width": "98%", "display": "inline-block"})
    ])
])

if __name__ == "__main__":
    app.run(debug=True)

