import ccxt

exchange_id = 'vinex'
exchange_class = getattr(ccxt, exchange_id)
print(exchange_class)

vinex = ccxt.vinex()
print(vinex.fetch_ticker('BTC/USDT'))

