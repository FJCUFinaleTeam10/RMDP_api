from django.db import models


# Create your models here.
class driver(models.Model):
    longitude = models.CharField(max_length=100)
    latitude = models.CharField(max_length=100)
    velocity = models.FloatField()
    capacity = models.FloatField()

    class Meta:
        db_table = "driver"
