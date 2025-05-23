from django.contrib.auth.models import Group, User
from rest_framework import serializers
from api.models import Currency, CurrencyExchangeRate, CurrencyExchangeRateProvider


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code', 'name', 'symbol']

class CurrencyExchangeRateProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchangeRateProvider
        fields = ['id', 'name', 'is_active', 'priority', 'api_key']

class CurrencyExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchangeRate
        fields = ['id', 'source_currency', 'target_currency', 'valuation_date', 'rate_value', 'provider']

class ConversionSerializer(serializers.ModelSerializer):
    source_currency = serializers.CharField(max_length=3)
    target_currency = serializers.CharField(max_length=3)
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)