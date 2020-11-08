from djmoney.contrib.exchange.backends import OpenExchangeRatesBackend

backend = OpenExchangeRatesBackend
backend.update_rates()