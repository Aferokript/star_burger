from django.db import models

from foodcartapp.models import Restaurant


class Places(models.Model):
    address = models.CharField(
        max_length=255, unique=True, null=True, verbose_name="Адрес"
    )
    lat = models.FloatField(verbose_name="Широта", null=True, blank=True)
    lon = models.FloatField(verbose_name="Долгота", null=True, blank=True)
    request_date = models.DateField(verbose_name="Дата запроса", null=True, blank=True)

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"

    def __str__(self):
        return f"{self.address} {self.lat} {self.lon}"
