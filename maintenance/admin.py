from django.contrib import admin
from .models import Vehicle, MaintenanceRecord

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("make", "model", "year", "vin", "user")
    search_fields = ("make", "model", "vin")
    list_filter = ("year",)


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "service_type", "date", "mileage")
    search_fields = ("vehicle__make", "vehicle__model", "service_type")
    list_filter = ("service_type", "date")
