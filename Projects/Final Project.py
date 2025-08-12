


import pandas as pd
import requests
#These lines import the required packages


#Zack's portion

API_KEY = "25ef9f82c4a9f4a53fd45be2d8bc255a"
SYMBOLS= ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META","TSLA", "AMD", "INTC", "F"]

DATE_FROM = '2025-04-28'
DATE_TO = '2025-07-28'
#url = (f"http://api.marketstack.com/v1/eod"f"?access_key={API_KEY}"f"&symbols={symbols_str}"f"&date_from={DATE_FROM}"f"&date_to={DATE_TO}")
url = "http://api.marketstack.com/v1/eod"
request_limit = 1000
# these lines define the variables needed to pull the desired data from the API
def fetch_EOD(symbols, start_date, end_date, api_key):
  all_rows= []
  symbols_str = ",".join(symbols)
  offset = 0

while True:
  params = {"access_key":api_key,
            "symbols":symbols_str,
            "date_to": end_date,
            "date_from": start_date,
            "limit": request_limit,
            "offset": offset}
r = requests.get(url, params=params, timeout=30)
r.raise_for_status()
data = r.json()
rows = data.get("data",[])
if not rows:
  break 
all_rows.extend(rows)
if len(rows) < limit:
  break
offset += limit
#end of Zack's portion


#michelle portion
import requests
import pandas as pd
from datetime import datetime
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# In case it fails it returns an empty dataframe

except Exception as f:
    print("Download warning:", f)
    return pd.DataFrame(columns=["symbol", "date", "high", "close", "low", "volume"])

    if not rows_all:
        return pd.DataFrame(columns=["symbol", "date", "high", "close", "low", "volume"])

# creating a DataFrame and only keeping the required columns while N/A values are filled 
    df = pd.DataFrame(rows_all)
    required = ["symbol", "date", "high", "close", "low", "volume"]
    for col in needed:
        if col not in df.columns:
            df[col] = pd.NA
    df = df[required].copy()

    # the datetime needed to be changed to allow it to properly pulled in the correct format and drop any values that will throw errors due to formatting
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    df = df.dropna(subset=["date"])  
    df["date"] = df["date"].dt.tz_convert(None)

    # Sort for plotting the data
    df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
    return df

#creating the dashboard
app = Dash(__name__)
app.title = "Stock Performance Dashboard"

app.layout = html.Div(
  style={"maxWidth": "1100px", "margin": "0 auto"},
  children=[html.H1("Stock Performance Dashboard", style={"textAlign": "center"}),
            html.Div(
              style={"display"=s "flex","alignItems":"flex end"},
  children=[html.Div(style={"flex": "1 1 320px", "minWidth": "280px"},
                     children=[html.Label("Select only two tickers:"),
                     dcc.Dropdown(id="compare-tickers",
                                  options=[{"label":s, "value":s} for s in sorted(df["symbol"].unique())],
                                  value=["AAPL", "MSFT"],
                                  multi=True
                                 ),
                               html.Div( "Tip: Choose exactly two tickers to compare their mean high.",
                                        style={"fontSize": "12px", "color": "#555", "marginTop": "6px"})]),
                                html.Div(style={"flex": "1 1 320px", "minWidth": "280px"},
                        children=[
                        html.Label("Select date range (within downloaded window):"),
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
                            style={"fontSize": "12px", "marginTop": "6px"})])]),
                        html.Hr(),
                        html.H1("Daily High (Time-Series Context)"),
                        dcc.Graph(id="timeseries-high", config={"displayModeBar": True}),
                        html.H2("Mean High Comparison Bar Chart)"),
                        dcc.Graph(id="mean-high-output", config={"displayModeBar": True})])

def _validate_selection(tickers):
    if not tickers:
        return False, "Please select two tickers."
    if len(tickers) != 2:
        return False, f"Please select exactly two tickers (current selection: {len(tickers)})."
    return True, "
  
def _filter_data(df, tickers, start_date, end_date):

    if df.empty:
        return df.copy()

    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    mask = (
        df["symbol"].isin(tickers)
        & (df["date"] >= start)
        & (df["date"] <= end)
    )
    return df.loc[mask].copy()

@app.callback(
    Output("timeseries-high", "figure"),
    Output("mean-high-output", "figure"),
    Input("compare-tickers", "value"),
    Input("date-picker", "start_date"),
    Input("date-picker", "end_date"),
)
def update_figures(tickers, start_date, end_date):

  # Validate selection
    ok, msg = _validate_selection(tickers)
    if not ok:
        empty_fig = {
            "data": [],
            "layout": {
                "title": msg,
                "xaxis": {"visible": False},
                "yaxis": {"visible": False},
                "annotations": [{
                    "text": msg,
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 16}
                }]
            },
        }
        return empty_fig, empty_fig

    
    filtered = _filter_data(df_all, tickers, start_date, end_date)

    if filtered.empty:
        msg = f"No data for {tickers} between {start_date} and {end_date}."
        empty_fig = {
            "data": [],
            "layout": {
                "title": msg,
                "xaxis": {"visible": False},
                "yaxis": {"visible": False},
                "annotations": [{
                    "text": "Try adjusting the date range.",
                    "xref": "paper",
                    "yref": "paper",
                    "showarrow": False,
                    "font": {"size": 16}
                }]
            },
        }
        return empty_fig, empty_fig
      
#creating a line graph to show general daily high across a time range

   fig = px.line(
        filtered,
        x="date",
        y="high",
        color="symbol",
        markers=True,
        labels={"date": "Date", "high": "Daily High (USD)", "symbol": "Ticker"},
        title=f"Daily High for {tickers[0]} vs {tickers[1]} ({start_date} → {end_date})")

#defining mean high
    mean_high = (
        filtered.groupby("symbol", as_index=False)["high"]
        .mean()
        .rename(columns={"high": "mean_high"}))

#creating a bar chart to show the mean high comparison of two symbols across a date range
    bar_fig = px.bar(
        mean_high,
        x="symbol",
        y="mean_high",
        text="mean_high",
        labels={"symbol": "Ticker", "mean_high": "Mean High (USD)"},
        title=f"Mean High Comparison ({start_date} → {end_date})")

    return fig, bar_fig

if __name__ == "__main__":
    app.run(debug=True)
#end of michelle portion                          



