from django.core.management.base import BaseCommand
from api.currency_adapters import ExchangeRateService  # Adjust import as needed
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Fetches exchange rates from CurrencyBeacon'

    def handle(self, *args, **kwargs):
        service = ExchangeRateService()
        today = datetime.today()
        currencies = ['USD', 'EUR', 'GBP']  # customize as needed

        for base in currencies:
            for target in currencies:
                if base != target:
                    self.stdout.write(f'Fetching rate {base} -> {target}')
                    try:
                        service.get_exchange_rate_data(base, target, today)
                        self.stdout.write(self.style.SUCCESS(f'Success: {base} -> {target}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Failed: {base} -> {target}: {e}'))
