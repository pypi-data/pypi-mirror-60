from django.db import models


# Create your models here.
class SubscriberModel(models.Model):
    first_name = models.CharField(max_length=12, null=True, blank=True)
    last_name = models.CharField(max_length=12, null=True, blank=True)
    username = models.CharField(max_length=15, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    mobile_number = models.PositiveIntegerField(null=True, blank=True)
    email = models.EmailField(max_length=75)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
