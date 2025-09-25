from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Vehicle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    vin = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"


class MaintenanceRecord(models.Model):
    SERVICE_TYPES = [
        ('oil_change', 'Oil Change'),
        ('tire_rotation', 'Tire Rotation'),
        ('tire_pressure', 'Tire Pressure Check'),
        ('fluid_check', 'Fluid Level Check'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="maintenance_records")
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    date = models.DateField()
    mileage = models.IntegerField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.vehicle} - {self.get_service_type_display()} ({self.date})"