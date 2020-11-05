from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'YOUR DATABASE NAME',
        'USER': 'YOUR POSTGRES USER',
        'PASSWORD': 'YOUR POSTGRES PASSWORD',
        'HOST': 'localhost'
    }
}

OPEN_EXCHANGE_RATES_APP_ID = 'YOUR APP ID FOR openexchangerates.org'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'YOUR SECRET KEY'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []