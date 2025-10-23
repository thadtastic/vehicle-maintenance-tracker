# maintenance/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Vehicle, MaintenanceRecord
from .serializers import VehicleSerializer, MaintenanceRecordSerializer
from .forms import VehicleForm  # keep this import for possible server-side forms


# -----------------------
# DRF API ViewSets
# -----------------------
class VehicleViewSet(viewsets.ModelViewSet):
    """
    API for Vehicles:
    - Only returns vehicles owned by the requesting user.
    - On create, the user is auto-assigned.
    """
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Limit results to the current user's vehicles
        return Vehicle.objects.filter(user=self.request.user).order_by('make', 'model', 'year')

    def perform_create(self, serializer):
        # Save vehicle with the current user attached
        serializer.save(user=self.request.user)


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    """
    API for MaintenanceRecord:
    - Only returns records linked to vehicles owned by the requesting user.
    - On create, verify the vehicle belongs to the requesting user.
    """
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only records for vehicles owned by the requesting user
        return MaintenanceRecord.objects.filter(vehicle__user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        vehicle = serializer.validated_data.get('vehicle')
        # Defensive check: ensure the vehicle belongs to the logged-in user
        if vehicle.user != self.request.user:
            raise PermissionDenied("You cannot create a maintenance record for a vehicle you do not own.")
        serializer.save()


# -----------------------
# Minimal page views (HTML) for UI
# -----------------------
@login_required
def add_vehicle_page(request):
    """
    Renders the front-end page that contains the JS UI for creating a vehicle.
    The page's JavaScript will POST JSON to /api/vehicles/ (DRF VehicleViewSet).
    """
    return render(request, "vehicles/add_vehicle_ui.html")


@login_required
def vehicle_list(request):
    """
    Optional: server-rendered list of vehicles for the current user.
    (Useful if you want both a JS UI and a simple server-side page.)
    """
    vehicles = Vehicle.objects.filter(user=request.user).order_by('make', 'model', 'year')
    return render(request, "vehicles/list.html", {"vehicles": vehicles})


@login_required
def vehicle_detail(request, pk):
    """
    Optional: server-rendered vehicle detail + maintenance records.
    """
    vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)
    maintenance_records = vehicle.maintenance_records.all().order_by('-date')
    return render(request, "vehicles/detail.html", {
        "vehicle": vehicle,
        "maintenance_records": maintenance_records
    })


@login_required
def vehicle_create(request):
    """
    Optional: server-side create (non-AJAX). Keeps for completeness — JS UI can skip this.
    """
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            v = form.save(commit=False)
            v.user = request.user
            v.save()
            return redirect('maintenance:vehicle_detail', pk=v.pk)
    else:
        form = VehicleForm()
    return render(request, "vehicles/form.html", {"form": form, "action": "Create"})


@login_required
def vehicle_update(request, pk):
    """
    Optional: server-side edit view.
    """
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if vehicle.user != request.user:
        return HttpResponseForbidden("You do not have permission to edit this vehicle.")

    if request.method == "POST":
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            return redirect('maintenance:vehicle_detail', pk=vehicle.pk)
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, "vehicles/form.html", {"form": form, "action": "Edit"})


@login_required
def vehicle_delete(request, pk):
    """
    Optional: confirm and delete a vehicle.
    """
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if vehicle.user != request.user:
        return HttpResponseForbidden("You do not have permission to delete this vehicle.")

    if request.method == "POST":
        vehicle.delete()
        return redirect('maintenance:vehicle_list')

    return render(request, "vehicles/confirm_delete.html", {"vehicle": vehicle})
