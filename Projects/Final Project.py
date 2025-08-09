


import pandas as pd
import requests
#These lines import the required packages


#Zack's portion

API_KEY = "1e2818762094064f311ceb8819ae47fb"
SYMBOL = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "BRK.B", "TSLA", "LLY", "AVGO",
    "JPM", "V", "UNH", "JNJ", "WMT", "PG", "MA", "XOM", "HD", "MRK",
    "ABBV", "ORCL", "COST", "CVX", "PEP", "BAC", "KO", "ADBE", "NVO", "TMO",
    "NFLX", "ACN", "LIN", "MCD", "ABT", "DHR", "INTC", "TM", "VZ", "CSCO",
    "DIS", "PFE", "NVS", "CRM", "T", "BHP", "SAP", "AMD", "RY", "SHEL"]
DATE_FROM = '2025-06-28'
DATE_TO = '2025-07-28'
url = (
    f"http://api.marketstack.com/v1/eod"
    f"?access_key={API_KEY}"
    f"&symbols={symbol}"
    f"&date_from={DATE_FROM}"
    f"&date_to={DATE_TO}")
# these lines define the variables needed to pull the desired data from the API

r = requests.get(url)
data = r.json()
print(data)
# These lines pull the requested data from the API

df = pd.DataFrame(data['data'])
df = df[['symbol','date','high']]

#end of Zacks portion


