from dotenv import load_dotenv
import json
import os
import requests
import datetime
import statistics
import csv

load_dotenv()

def to_usd(my_price):
    return "${0:,.2f}".format(my_price)

ticker_input = input('Please enter a valid Stock Symbol(ex. AMZN): ')


symbol = ticker_input
api_key = os.environ.get("ALPHAVANTAGE_API_KEY")
request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"

response = requests.get(request_url)

parsed_response = json.loads(response.text)

last_refreshed = parsed_response["Meta Data"]["3. Last Refreshed"]
now = datetime.datetime.now()

tsd = parsed_response["Time Series (Daily)"]
dates = list(tsd.keys()) #assume last day is first in list of dates
latest_day = dates[0] 
latest_close = tsd[latest_day]["4. close"]

high_prices = []
low_prices = []

for date in dates:
    high_price = tsd[date]["2. high"]
    high_prices.append(float(high_price))
    low_price = tsd[date]["3. low"]
    low_prices.append(float(low_price))

recent_high = max(high_prices)
recent_low = min(low_prices)


#
# INFO OUTPUTS
#

#csv_file_path = "data/prices.csv"

csv_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "prices.csv")

csv_headers = ["timestamp", "open", "high", "low", "close", "volume"]

with open(csv_file_path, "w") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
    writer.writeheader() 
    for date in dates:
        daily_prices = tsd[date]
        writer.writerow({
            "timestamp": date,
            "open": daily_prices["1. open"],
            "high": daily_prices["2. high"],
            "low": daily_prices["3. low"],
            "close": daily_prices["4. close"],
            "volume": daily_prices["5. volume"],
        })





print("----------------------------------")
print(f"STOCK SYMBOL: {symbol}")
print("RUN AT: " +now.strftime("%Y-%m-%d %H:%M:%S"))
print("----------------------------------")
print(f"LATEST UPDATE: {last_refreshed}")
print(f"LATEST CLOSE: {to_usd(float(latest_close))}")
print(f"RECENT HIGH: {to_usd(float(recent_high))}")
print(f"RECENT LOW: {to_usd(float(recent_low))}")
print("----------------------------------")

threshold = 1.2*float(recent_low)
if float(latest_close) < threshold:
    print("RECOMMENDATION: BUY!")
    print("RECOMMENDATION REASON: The latest closing price is not larger than 20 percent of the recent low")
else:
    print("RECOMMENDATION: DONT BUY!")
    print("RECOMMENDATION REASON: The latest closing price is larger than 20 percent of the recent low")
print("----------------------------------")
print(f"WRITING DATA TO CSV: {csv_file_path}...")
