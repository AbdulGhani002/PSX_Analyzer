import requests

def fetch_tickers_metadata():
	response = requests.get("https://dps.psx.com.pk/symbols")
	if response.status_code != 200:
		return None
	return response.json()

def fetch_data(ticker):
	response = requests.get(f"https://dps.psx.com.pk/timeseries/int/{ticker}")
	if response.status_code != 200:
		return None
	return response.json()



# print(fetch_data('MEBL'))
# print(fetch_tickers_metadata()[0]['symbol'])

def filter_symbols(tickers_object_list):
	ticker_symbols = []
	for ticker_metadata in tickers_object_list:
		if ticker_metadata['isDebt'] == False:
			ticker_symbols.append(ticker_metadata['symbol'])
	return ticker_symbols
 
def fetch_ticker_data_all(tickers_list):
	for ticker in tickers_list:
		print(ticker)
		ticker_data = fetch_data(ticker)
		print(ticker_data)
print(fetch_ticker_data_all(filter_symbols(fetch_tickers_metadata())))

