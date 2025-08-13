import pandas as pd
import requests
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# --- Zack's portion (fixed) ---
"""
PARAMETERS
---------------
symbols: list of str
list of stock symbols to fetch 
start_date: str
start date in YYYY-MM-DD format.
end date in YYYY-MM-DD format.
api_key = str
API key for accessing the API
"""

API_KEY = "25ef9f82c4a9f4a53fd45be2d8bc255a"
SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AMD", "INTC", "F"]
DATE_FROM = '2025-01-01'
DATE_TO = '2025-08-01'
URL = "http://api.marketstack.com/v1/eod"
REQUEST_LIMIT = 1000

#Fetch EOD stock price data for tickers within a date range.


def fetch_EOD(symbols, start_date, end_date, api_key):
    """
    Returns:
    -------
    list of dict
    A list of dictionaries containing EOD stock data with keys such as 'symbol', 'date from', 'high', 'date to', and 'close','low'.
    
    """
    
    all_rows = []
    symbols_str = ",".join(symbols)
    offset = 0

    while True:
        params = {
            "access_key": api_key,
            "symbols": symbols_str,
            "date_to": end_date,
            "date_from": start_date,
            "limit": REQUEST_LIMIT,
            "offset": offset
        }
        r = requests.get(URL, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        rows = data.get("data", [])
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < REQUEST_LIMIT:
            break
        offset += REQUEST_LIMIT

    return all_rows

# --- Michelle's portion (fixed) ---

# Attempt to get the data fetch EOD stock price 
try:
    rows_all = fetch_EOD(SYMBOLS, DATE_FROM, DATE_TO, API_KEY)

    if not rows_all:
        df = pd.DataFrame(columns=["symbol", "date", "high", "close", "low"])
    else:
        df = pd.DataFrame(rows_all)
        required = ["symbol", "date", "high", "close", "low"]
        for col in required:
            if col not in df.columns:
                df[col] = pd.NA
        df = df[required].copy()

        df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
        df = df.dropna(subset=["date"])
        df["date"] = df["date"].dt.tz_convert(None) #change the time zone so that it doesnt give an error

        df = df.sort_values(["symbol", "date"]).reset_index(drop=True)

except Exception as e:
    print("Download warning:", e)
    df = pd.DataFrame(columns=["symbol", "date", "high", "close", "low"]) # counting for an error if it occurs

#Ayesha's Portion

def average_top10_high(df):
    """
    Returns the average 'high' price for the top 10 stocks ranked by mean high.
    """
    if df.empty:
        return 0.0
    mean_high_per_stock = df.groupby("symbol", as_index=False)["high"].mean()
    top10 = mean_high_per_stock.sort_values(by="high", ascending=False).head(10)
    return top10["high"].mean()


def top10_highest_volatility(df):
    """
    Returns a DataFrame of the top 10 stocks with the highest volatility
    (standard deviation of daily high prices).
    """
    if df.empty:
        return pd.DataFrame(columns=["symbol", "volatility"])
    vol_per_stock = df.groupby("symbol", as_index=False)["high"].std()
    vol_per_stock = vol_per_stock.rename(columns={"high": "volatility"})
    return vol_per_stock.sort_values(by="volatility", ascending=False).head(10)


#Michelle portion-Dash App Starts here-------


app = Dash(__name__)
app.title = "Stock Performance Dashboard"

app.layout = html.Div(
    style={"maxWidth": "1100px", "margin": "0 auto", "padding": "14px"},
    children=[
        html.H1("Stock Performance Dashboard", style={"textAlign": "center"}),

        html.Div(
            style={"display": "flex", "alignItems": "flex-end", "gap": "14px"},
            children=[
                html.Div(
                    style={"flex": "1 1 320px", "minWidth": "280px"},
                    children=[
                        html.Label("Select only two tickers:"),
                        dcc.Dropdown(
                            id="compare-tickers",
                            options=[{"label": s, "value": s} for s in sorted(df["symbol"].unique())],
                            value=["AAPL", "MSFT"],
                            multi=True
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Label("Select date range (within window):"),
                        dcc.DatePickerRange(
                            id="date-picker",
                            start_date=DATE_FROM,
                            end_date=DATE_TO,
                            display_format="YYYY-MM-DD",
                            min_date_allowed=DATE_FROM,
                            max_date_allowed=DATE_TO,
                        ),
                        html.Div(
                            f"Available data window: {DATE_FROM} → {DATE_TO}",
                            style={"fontSize": "12px", "marginTop": "6px"},
                        ),
                    ]
                ),
            ]
        ),
        html.Hr(),
        html.H2("Daily High (Time-Series Context)"),
        dcc.Graph(id="timeseries-high", config={"displayModeBar": True}),
        html.H2("Mean High Comparison Bar Chart"),
        dcc.Graph(id="mean-high-output", config={"displayModeBar": True}),

        html.H3(f"Average 'High' Price (Top 10 Stocks): {average_top10_high(df):.2f} USD",
                style={"textAlign": "center", "color": "darkblue"}),

        html.H3("Top 10 Most Volatile Stocks (Std Dev of High Price):",
                style={"textAlign": "center", "color": "darkred"}),

        dcc.Graph(
            figure=px.bar(
                top10_highest_volatility(df),
                x="symbol",
                y="volatility",
                text_auto=True,
                labels={"symbol": "Ticker", "volatility": "Volatility (Std Dev)"},
                title="Top 10 Most Volatile Stocks"
            )
        ),
    ]
)


def _validate_selection(tickers):
"""
validate that exactly two tickers are selected.

Parameters
--------------
tickers: list of str
- list of selected ticker symbols return limit of 1000

Returns
---------------
tuple
(boolean,str) where the boolean indicates if the selection is valid and string shows an error message if it is invalid.
"""
    if not tickers:
        return False, "Please select two tickers."
    if len(tickers) != 2:
        return False, f"Please select exactly two tickers (current selection: {len(tickers)})."
    return True, ""

def _filter_data(df_input, tickers, start_date, end_date):
"""
PARAMETERS:
---------------
df_input: Pandas data frame which contains the stock data
tickers: list of str, 
selected tickers to filter by
start_date: str
start date: in YYYY-MM-DD format.
end date: str
in YYYY-MM-DD format.

RETURNS:
----------------
pandas.Dateframe
filter the stock data by selected 2 tickers and date range.

"""
    if df_input.empty:
        return df_input.copy()
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    mask = (
        df_input["symbol"].isin(tickers) &
        (df_input["date"] >= start) &
        (df_input["date"] <= end)
    )
    return df_input.loc[mask].copy()

# --- Main Callback ---

@app.callback(
    Output("timeseries-high", "figure"),
    Output("mean-high-output", "figure"),
    Input("compare-tickers", "value"),
    Input("date-picker", "start_date"),
    Input("date-picker", "end_date"),
)
def update_figures(tickers, start_date, end_date):
"""
Update the dashboard based on selected tickers and date range 

Parameters
------------
tickers:list of str
selected tickers to filter by
start_date: str
start date in YYYY-MM-DD format.
end date: str
in YYYY-MM-DD format.

Returns
-------------
tuple 
(fig _timeseries, fig_bar) where both are Plotly figures
if selection or data is invalid , returns empty figures with error messages
"""

    ok, msg = _validate_selection(tickers)
    if not ok:
        empty_fig = {
            "data": [],
            "layout": {
                "title": msg,
                "xaxis": {"visible": False},
                "yaxis": {"visible": False}
            }
        }
        return empty_fig, empty_fig

    filtered = _filter_data(df, tickers, start_date, end_date)

    if filtered.empty:
        msg = f"No data for {tickers} between {start_date} and {end_date}."
        empty_fig = {
            "data": [],
            "layout": {
                "title": msg,
                "xaxis": {"visible": False},
                "yaxis": {"visible": False}
            }
        }
        return empty_fig, empty_fig

    fig = px.line(
        filtered,
        x="date",
        y="high",
        color="symbol",
        markers=True,
        labels={"date": "Date", "high": "Daily High (USD)", "symbol": "Ticker"},
        title=f"Daily High for {tickers[0]} vs {tickers[1]} ({start_date} → {end_date})",
    )

    mean_high = (
        filtered.groupby("symbol", as_index=False)["high"]
        .mean()
        .rename(columns={"high": "mean_high"})
    )

    bar_fig = px.bar(
        mean_high,
        x="symbol",
        y="mean_high",
        text_auto=True,
        labels={"symbol": "Ticker", "mean_high": "Mean High (USD)"},
        title=f"Mean High Comparison ({start_date} → {end_date})",
    )

    return fig, bar_fig

# --- Run Server ---
if __name__ == "__main__":
    app.run(debug=True)
