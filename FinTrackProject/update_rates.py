import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FinTrack.settings')
django.setup()
from djmoney.contrib.exchange.backends import OpenExchangeRatesBackend

backend = OpenExchangeRatesBackend()
backend.update_rates()
