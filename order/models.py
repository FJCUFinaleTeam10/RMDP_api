from django.db import models

# Create your models here.
from driver.models import driver
from restaurant.models import restaurant


class order(models.Model):
    timeRequest = models.DateTimeField(null=True)
    loadToDriver = models.BooleanField()
    longitude = models.CharField(max_length=100)
    latitude = models.CharField(max_length=100)
    deadlineTime = models.DateTimeField()
    restaurantId = models.ForeignKey(restaurant, on_delete=models.CASCADE)
    arriveTime = models.DateTimeField()
    driverId = models.ForeignKey(driver, on_delete=models.CASCADE)

    class Meta:
        db_table = "order"

# Create your models here.
