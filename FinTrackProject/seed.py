
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FinTrack.settings')
django.setup()

from Main.models import Currency
from djmoney.contrib.exchange.backends import OpenExchangeRatesBackend

Currency.objects.get_or_create(name='USD', long_name='United States Dollar')
Currency.objects.get_or_create(name='ILS', long_name='New Israeli Shekel')

backend = OpenExchangeRatesBackend()
backend.update_rates()