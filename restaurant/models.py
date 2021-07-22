from django.db import models


# Create your models here.
class restaurant(models.Model):
    longitude = models.CharField(max_length=100)
    latitude = models.CharField(max_length=100)

    class Meta:
        db_table = "restaurant"
