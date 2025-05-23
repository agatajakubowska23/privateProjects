from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from api import views
from api.models import CurrencyExchangeRateProvider

router = routers.DefaultRouter()
router.register(r'currencies', views.CurrencyViewSet)
router.register(r'providers', views.CurrencyExchangeRateProviderViewSet)
router.register(r'exchange-rate', views.CurrencyExchangeRateViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
