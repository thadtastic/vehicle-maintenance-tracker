from django import forms
from .models import Vehicle, MaintenanceRecord

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["make", "model", "year", "vin"]


class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = ["vehicle", "service_type", "date", "mileage", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"})
        }
