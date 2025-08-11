


import pandas as pd
import requests
#These lines import the required packages


#Zack's portion

API_KEY = "1e2818762094064f311ceb8819ae47fb"
SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META","TSLA", "AMD", "INTC", "F"]
symbols_str = ",".join(SYMBOLS)
DATE_FROM = '2025-04-28'
DATE_TO = '2025-07-28'
url = (f"http://api.marketstack.com/v1/eod"f"?access_key={API_KEY}"f"&symbols={symbols_str}"f"&date_from={DATE_FROM}"f"&date_to={DATE_TO}")
# these lines define the variables needed to pull the desired data from the API

r = requests.get(url)
data = r.json()
# These lines pull the requested data from the API

df = pd.DataFrame(data['data'])
df = df[['symbol','date','high','close','low','volume']]
#end of Zack's portion


