from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, List
from django.core.cache import cache
import requests
import random
from api.models import CurrencyExchangeRateProvider, CurrencyExchangeRate, Currency


class ExchangeRateProviderBase(ABC):

    @abstractmethod
    def get_exchange_rate_data(self, source_currency: str, target_currency: str, valuation_date: datetime):
        pass

    def get_rates_for_period(self, source_currency: str,
                             date_from: datetime, date_to: datetime) -> List[Dict]:
        pass


class CurrencyBeaconProvider(ExchangeRateProviderBase):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://api.currencybeacon.com/v1'


    def get_exchange_rate_data(self, source_currency: str, target_currency: str, valuation_date: datetime)-> Optional[Dict]:
        try:
            date_str = valuation_date.strftime('%Y-%m-%d')

            endpoint = f'{self.base_url}/historical'
            params = {
                'api_key': self.api_key,
                'base': source_currency,
                'date': date_str,
                'symbols': target_currency
            }

            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            return {
                    'source_currency': source_currency,
                    'target_currency': target_currency,
                    'rate_value': Decimal(data['rates'][target_currency]),
                    'date': date_str,
                    'provider':  'currencybeacon'
            }

        except Exception as e:
            raise Exception(f'CurrencyBeacon API error: {str(e)}')

    def get_rates_for_period(self, source_currency: str, date_from: datetime,
                                 date_to: datetime) -> List[Dict]:
        try:
            endpoint = f'{self.base_url}/timeseries'
            params = {
                'api_key': self.api_key,
                'base': source_currency,
                'start_date': date_from.strftime('%Y-%m-%d'),
                'end_date': date_to.strftime('%Y-%m-%d')
            }
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            return [
                {
                    'source_currency': source_currency,
                    'rates':{curr: Decimal(str(rate)) for curr, rate in rates.items()},
                    'date': date,
                    'provider': 'currencybeacon'
                } for date, rates in data.items()
            ]
        except Exception as e:
            raise Exception(f'CurrencyBeacon API error: {str(e)}')


class MockExchangeRateProvider(ExchangeRateProviderBase):

    def get_exchange_rate_data(self, source_currency: str, target_currency: str, valuation_date: datetime)-> Optional[Dict]:
        rate = Decimal(str(round(random.uniform(0.5, 2.0), 6)))

        return {
            'source_currency': source_currency,
            'target_currency': target_currency,
            'rate_value': rate,
            'date': valuation_date.strftime('%Y-%m-%d'),
            'provider': 'mock'
        }

    def get_rates_for_period(self, source_currency: str, date_from: datetime,
                            date_to: datetime, provider: str = None) -> List[Dict]:

        rates = []
        current_date = date_from

        while current_date <= date_to:
            currencies = Currency.objects.exclude(code=source_currency)
            daily_rates = {
                curr.code: Decimal(str(round(random.uniform(0.5, 2.0), 6)))
                for curr in currencies
            }

            rates.append({
                'source_currency': source_currency,
                'rates': daily_rates,
                'date': current_date.strftime("%Y-%m-%d"),
                'provider': 'mock'
            })
            current_date += timedelta(days=1)

        return rates


class ExchangeRateService:
    def __init__(self):
        self._provider_instance = {}
        self._provider_order = []
        self.refresh_providers()

    def refresh_providers(self):
        providers = CurrencyExchangeRateProvider.objects.filter(is_active=True).order_by('-priority')

        self._provider_instance = {}
        self._provider_order = []

        if providers.exists():
            for provider in providers:
                if provider.name == 'currencybeacon':
                    self._provider_instance['currencybeacon'] = CurrencyBeaconProvider(provider.api_key)
                    self._provider_order.append('currencybeacon')
        else:
            self._provider_instance['mock'] = MockExchangeRateProvider()
            self._provider_order = ['mock']

    def _get_provider(self, provider_name: Optional[str] = None) -> ExchangeRateProviderBase:
        if provider_name:
            provider = self._provider_instance.get(provider_name)
            if not provider:
                raise ValueError(f"Provider '{provider_name}' not found or inactive.")
            return provider

        for name in self._provider_order:
            provider = self._provider_instance.get(name)
            if provider:
                return provider

        return MockExchangeRateProvider()

    def get_exchange_rate_data(self, source_currency: str, target_currency: str,
                               valuation_date: datetime, provider: str = None) -> Dict:
        """Get exchange rate data with caching"""
        cache_key = f"rate: {source_currency} to {target_currency} on {valuation_date}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        provider_instance = self._get_provider(provider)
        rate_data = provider_instance.get_exchange_rate_data(
            source_currency, target_currency, valuation_date
        )

        cache.set(cache_key, rate_data, 3600)

        CURRENCY_METADATA = {
            'USD': {'name': 'US Dollar', 'symbol': '$'},
            'EUR': {'name': 'Euro', 'symbol': '€'},
            'GBP': {'name': 'British Pound', 'symbol': '£'},
            # Add more if needed
        }

        source_currency_obj, _ = Currency.objects.get_or_create(
            code=source_currency,
            defaults=CURRENCY_METADATA.get(source_currency, {'name': source_currency, 'symbol': source_currency})
        )

        target_currency_obj, _ = Currency.objects.get_or_create(
            code=target_currency,
            defaults=CURRENCY_METADATA.get(target_currency, {'name': target_currency, 'symbol': target_currency})
        )

        # Get provider object
        provider_name = provider or self._provider_order[0]

        source_currency_obj, _ = Currency.objects.get_or_create(
            code=source_currency,
            defaults=CURRENCY_METADATA.get(source_currency, {'name': source_currency, 'symbol': source_currency})
        )
        target_currency_obj, _ = Currency.objects.get_or_create(
            code=target_currency,
            defaults={'name': target_currency, 'symbol': target_currency}
)
        provider_obj, _ = CurrencyExchangeRateProvider.objects.get_or_create(
            name=provider_name,
            defaults={
                'priority': 0,
                'is_active': False,
                'api_key': ''
            }
)

        CurrencyExchangeRate.objects.update_or_create(
            source_currency=source_currency_obj,
            target_currency=target_currency_obj,
            valuation_date=valuation_date,
            provider=provider_obj,
            defaults={
                'rate_value': rate_data['rate_value'],
            }
        )

        return rate_data

    def get_rates_for_period(self, source_currency: str, date_from: datetime,
                             date_to: datetime, provider: str = None) -> List[Dict]:
        """Get exchange rates for a period with caching"""
        cache_key = f"rates_{source_currency}_{date_from}_{date_to}_{provider or 'default'}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        provider_instance = self._get_provider(provider)
        rates_data = provider_instance.get_rates_for_period(
            source_currency, date_from, date_to
        )
        cache.set(cache_key, rates_data, 3600)

        return rates_data




