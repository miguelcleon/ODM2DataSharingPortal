from django.contrib import admin

from dataloader.models import *


# Register your models here.
from dataloaderinterface.models import SiteRegistration, SiteSensor


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


@admin.register(EquipmentModel)
class EquipmentModelAdmin(admin.ModelAdmin):
    sensor_fields = ['model_name', 'variable_code']

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
