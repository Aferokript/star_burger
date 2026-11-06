from django.db import models

from foodcartapp.models import Restaurant


class RestaurantsPlace(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name="places",
        on_delete=models.CASCADE,
        verbose_name="Ресторан",
    )
    address = models.CharField(max_length=50, verbose_name="Адрес")
    lat = models.FloatField(verbose_name="Широта")
    lon = models.FloatField(verbose_name="Долгота")
    date_request = models.DateField(verbose_name="Дата запроса к Геокодеру")

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса "
        unique_together = ("restaurant", "address")

    def __str__(self):
        return f"{self.restaurant} {self.address} {self.lat} {self.lon}"
