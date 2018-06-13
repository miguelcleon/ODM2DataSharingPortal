from django.contrib import admin
from django import forms
from django.db.models.expressions import F

from dataloader.models import *


# Register your models here.
from dataloaderinterface.models import SiteRegistration, SiteSensor, SensorOutput
from hydroshare.models import HydroShareAccount, HydroShareResource
from leafpack.models import LeafPack, LeafPackType, Macroinvertebrate


def update_sensor_data(obj, form, sensor_fields):
    old_object = obj.__class__.objects.get(pk=obj.pk)
    old_data = {field: getattr(old_object, field) for field in sensor_fields}
    new_data = {field: getattr(obj, field) for field in form.changed_data}
    SensorOutput.objects.annotate(equipment_model_id=F('model_id')).filter(**old_data).update(**new_data)


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
    sensor_fields = ['equipment_model_id']

    def save_model(self, request, obj, form, change):
        if change:
            update_sensor_data(obj, form, self.sensor_fields)

        super(EquipmentModelAdmin, self).save_model(request, obj, form, change)


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    sensor_fields = ['variable_id']

    def save_model(self, request, obj, form, change):
        if change:
            update_sensor_data(obj, form, self.sensor_fields)

        super(VariableAdmin, self).save_model(request, obj, form, change)


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    sensor_fields = ['unit_id']

    def save_model(self, request, obj, form, change):
        if change:
            update_sensor_data(obj, form, self.sensor_fields)

        super(UnitAdmin, self).save_model(request, obj, form, change)


@admin.register(InstrumentOutputVariable)
class InstrumentOutputVariableAdmin(admin.ModelAdmin):
    pass


class SensorOutputForm(forms.ModelForm):
    model_id = forms.ModelChoiceField(queryset=EquipmentModel.objects.all(), label='Equipment Model')
    variable_id = forms.ModelChoiceField(queryset=Variable.objects.all(), label='Variable')
    unit_id = forms.ModelChoiceField(queryset=Unit.objects.all(), label='Unit')
    sampled_medium = forms.ModelChoiceField(queryset=Medium.objects.all(), label='Sampled Medium')

    def clean_model_id(self):
        return self.data['model_id']

    def clean_variable_id(self):
        return self.data['variable_id']

    def clean_unit_id(self):
        return self.data['unit_id']

    class Meta:
        model = SensorOutput
        fields = ['model_id', 'variable_id', 'unit_id', 'sampled_medium']


@admin.register(SensorOutput)
class SensorOutputAdmin(admin.ModelAdmin):
    form = SensorOutputForm

    def save_model(self, request, obj, form, change):
        # creation and update do the same.
        equipment_model = EquipmentModel.objects.get(pk=form.data['model_id'])
        variable = Variable.objects.get(pk=form.data['variable_id'])
        unit = Unit.objects.get(pk=form.data['unit_id'])

        iov = InstrumentOutputVariable.objects.get_or_create(
            model=equipment_model,
            variable=variable,
            instrument_method=Method.objects.filter(method_code='Sensor').first(),
            instrument_raw_output_unit=unit
        )[0]
        obj.instrument_output_variable_id = iov.instrument_output_variable_id
        obj.model_name = equipment_model.model_name
        obj.model_manufacturer = equipment_model.model_manufacturer.organization_code
        obj.variable_name = variable.variable_name_id
        obj.variable_code = variable.variable_code
        obj.unit_name = unit.unit_name
        obj.unit_abbreviation = unit.unit_abbreviation
        obj.save()

        super(SensorOutputAdmin, self).save_model(request, obj, form, change)


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
