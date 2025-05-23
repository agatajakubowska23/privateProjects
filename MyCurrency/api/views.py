from datetime import datetime
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import  viewsets, status

from api.models import Currency, CurrencyExchangeRate, CurrencyExchangeRateProvider
from api.serializers import  (CurrencySerializer,
                              CurrencyExchangeRateSerializer,
                              ConversionSerializer, CurrencyExchangeRateProviderSerializer)
from api.currency_adapters import ExchangeRateService


class CurrencyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class CurrencyExchangeRateProviderViewSet(viewsets.ModelViewSet):
    queryset = CurrencyExchangeRateProvider.objects.all()
    serializer_class = CurrencyExchangeRateProviderSerializer

    @action(detail=True, methods=['POST'])
    def set_priority(self, request, pk=None):
        provider = self.get_object()
        priority = request.data.get('priority')

        if priority is None:
            return Response(
                {"error": "Priority is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        provider.priority = priority
        provider.save()

        exchange_rate_service = ExchangeRateService()
        exchange_rate_service.refresh_providers()

        return Response(self.get_serializer(provider).data)


class CurrencyExchangeRateViewSet(viewsets.ModelViewSet):
    queryset = CurrencyExchangeRate.objects.all()
    serializer_class = CurrencyExchangeRateSerializer

    def get_exchange_rate_service(self):
        return ExchangeRateService()
    # exchange_rate_service = ExchangeRateService()

    @action(detail=False, methods=['GET'])
    def get_exchange_rate(self, request):
        source_currency = request.query_params.get('source_currency')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        if not all([source_currency, date_from, date_to]):
            return Response(
                {'error': 'source_currency, date_from and date_to are required parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            rates = CurrencyExchangeRate.objects.filter(
                source_currency__code=source_currency,
                valuation_date__range=[date_from, date_to])
            serializer = self.get_serializer(rates, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['POST'])
    def convert(self, request):
        serializer = ConversionSerializer(data=request.data)
        if serializer.is_valid():
            source_currency = serializer.validated_data['source_currency']
            target_currency = serializer.validated_data['target_currency']
            amount = serializer.validated_data['amount']
            try:
                latest_rate = CurrencyExchangeRate.objects.filter(
                    source_currency__code=source_currency,
                    target_currency__code=target_currency
                ).latest('valuation_date')
                converted_amount = amount * latest_rate.rate_value
                return Response({
                    'source_currency': source_currency,
                    'target_currency': target_currency,
                    'amount': amount,
                    'converted_amount': converted_amount,
                    'rate': latest_rate.rate_value,
                    'date': latest_rate.valuation_date,
                })
            except CurrencyExchangeRate.DoesNotExist:
                return Response(
                    {
                        'error': 'No exchange rate found for the given currency pair'
                    }
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




