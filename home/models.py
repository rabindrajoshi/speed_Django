from django.db import models
#from django.contrib.postgres.fields import ArrayField
# Create your models here.
class Login(models.Model):
   number_plate=models.CharField(null=True,max_length=120)
   speed=models.CharField(max_length=15)
   s_speed=models.CharField(null=True,max_length=12)
   

   def __str__(self) :
      return self.number_plate


class Speed(models.Model):
    vehicle_number = models.CharField(max_length=15)
    speed = models.IntegerField()
    s_speed=models.IntegerField(null=True)

    def __str__(self):
        return self.vehicle_number
