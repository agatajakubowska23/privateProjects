from django.db import models
from django.core.exceptions import ValidationError

class ProtectedModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        if not self.can_be_deleted():
            raise ValidationError("This object cannot be deleted.")
        self.is_deleted = True
        self.save()

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def can_be_deleted(self):
        return True

    class Meta:
        abstract = True

class Currency(ProtectedModel):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100, blank=True)
    symbol = models.CharField(max_length=10, blank=True)

    def save(self, *args, **kwargs):
        currency_info = {
            'USD': ('United States Dollar', '$'),
            'EUR': ('Euro', '€'),
            'GBP': ('British Pound', '£'),
        }
        if self.code in currency_info:
            self.name, self.symbol = currency_info[self.code]
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "currencies"
    def __str__(self):
        return f"{self.code} - {self.name}"

class CurrencyExchangeRateProvider(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    api_key = models.CharField(max_length=255, blank=True)
    class Meta:
        ordering = ['-priority']
    def __str__(self):
        return self.name


class CurrencyExchangeRate(models.Model):
    source_currency = models.ForeignKey(Currency,related_name='exchanges',
    on_delete=models.CASCADE)
    target_currency = models.ForeignKey(Currency,on_delete=models.CASCADE)
    valuation_date = models.DateField()
    rate_value = models.DecimalField(decimal_places=6,max_digits=18)
    provider = models.ForeignKey(CurrencyExchangeRateProvider,on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('source_currency', 'target_currency', 'valuation_date', 'provider')
    def __str__(self):
        return f"{self.source_currency.code}/{self.target_currency.code}: {self.rate_value} ({self.valuation_date})"

