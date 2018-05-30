from __future__ import unicode_literals

from django.db import models
from django.db.models.aggregates import Max
from django.db.models.expressions import F
from django.db.models.query import Prefetch


class SiteRegistrationQuerySet(models.QuerySet):
    # TODO: put the status variables in a settings file so it's customizable.
    status_variables = ['EnviroDIY_Mayfly_Batt', 'EnviroDIY_Mayfly_Temp']

    def with_sensors(self):
        return self.prefetch_related('sensors')

    def with_status_sensors(self):
        # gets the SiteSensor class from the SiteRegistration model to avoid a circular import
        # don't try this at home, kids.
        sensor_model = [
            related_object.related_model
            for related_object in self.model._meta.related_objects
            if related_object.name == 'sensors'
        ].pop()

        return self.prefetch_related(Prefetch(
            lookup='sensors',
            queryset=sensor_model.objects.filter(variable_code__in=self.status_variables),
            to_attr='status_sensors'))

    def deployed_by(self, user_id):
        return self.filter(django_user_id=user_id)

    def followed_by(self, user_id):
        return self.filter(followed_by__id=user_id)

    def with_latest_measurement(self):
        return self.annotate(latest_measurement=Max('sensors__last_measurement__value_datetime'))


class SiteSensorQuerySet(models.QuerySet):
    pass


class SensorOutputQuerySet(models.QuerySet):
    def with_filter_names(self):
        return self.annotate(
            sensor_manufacturer=F('model_manufacturer'),
            sensor_model=F('model_id'),
            variable=F('variable_id'),
            unit=F('unit_id')
        )

    def for_filters(self):
        return self.with_filter_names().values(
            'pk',
            'sensor_manufacturer',
            'sensor_model',
            'variable',
            'unit',
            'sampled_medium'
        )
