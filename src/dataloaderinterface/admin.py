from django.contrib import admin

from dataloader.models import *


# Register your models here.
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    pass


@admin.register(EquipmentModel)
class EquipmentModelAdmin(admin.ModelAdmin):
    pass


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    pass


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    pass


@admin.register(InstrumentOutputVariable)
class InstrumentOutputVariableAdmin(admin.ModelAdmin):
    pass
