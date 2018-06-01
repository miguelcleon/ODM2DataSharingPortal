from django.contrib import admin

from dataloader.models import *


# Register your models here.
from dataloaderinterface.models import SiteRegistration, SiteSensor, HydroShareResource, HydroShareAccount, SensorOutput
from leafpack.models import LeafPack, LeafPackType, Macroinvertebrate


def update_sensor_data(obj, form, sensor_fields):
    old_object = obj.__class__.objects.get(pk=obj.pk)
    old_data = {field: getattr(old_object, field) for field in sensor_fields if field in form.changed_data}
    new_data = {field: getattr(obj, field) for field in sensor_fields if field in form.changed_data}
    SiteSensor.objects.filter(**old_data).update(**new_data)


@admin.register(SiteSensor)
class SiteSensorAdmin(admin.ModelAdmin):
    pass


@admin.register(SiteRegistration)
class SiteRegistrationAdmin(admin.ModelAdmin):
    pass


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    pass


@admin.register(EquipmentModel)
class EquipmentModelAdmin(admin.ModelAdmin):
    sensor_fields = ['model_name', 'model_manufacturer']

    def save_model(self, request, obj, form, change):
        if change:
            update_sensor_data(obj, form, self.sensor_fields)

        super(EquipmentModelAdmin, self).save_model(request, obj, form, change)


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    sensor_fields = ['variable_name', 'variable_code']

    def save_model(self, request, obj, form, change):
        if change:
            update_sensor_data(obj, form, self.sensor_fields)

        super(VariableAdmin, self).save_model(request, obj, form, change)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    sensor_fields = ['unit_name', 'unit_abbreviation']

    def save_model(self, request, obj, form, change):
        if change:
            update_sensor_data(obj, form, self.sensor_fields)

        super(UnitAdmin, self).save_model(request, obj, form, change)


@admin.register(InstrumentOutputVariable)
class InstrumentOutputVariableAdmin(admin.ModelAdmin):
    pass


@admin.register(SensorOutput)
class SensorOutputAdmin(admin.ModelAdmin):
    pass


class HydroShareResourceInline(admin.TabularInline):
    model = HydroShareResource


@admin.register(HydroShareAccount)
class HydroShareAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'ext_id', 'username', 'resources')
    fields = ('ext_id', 'token')


@admin.register(HydroShareResource)
class HydroShareResourceAdmin(admin.ModelAdmin):
    pass


@admin.register(LeafPack)
class LeafPackAdmin(admin.ModelAdmin):
    pass


@admin.register(LeafPackType)
class LeafPackTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Macroinvertebrate)
class MacroinvertebrateAdmin(admin.ModelAdmin):

    list_display = ('scientific_name', 'pollution_tolerance', 'common_name')

    def get_queryset(self, request):
        queryset = super(MacroinvertebrateAdmin, self).get_queryset(request)
        return queryset.order_by('pollution_tolerance')
