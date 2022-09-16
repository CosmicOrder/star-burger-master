from django.db import models


class Location(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
    )
    lat = models.FloatField('широта', null=True)
    lon = models.FloatField('долгота', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('lat', 'lon', 'address')

    def __str__(self):
        return self.address
