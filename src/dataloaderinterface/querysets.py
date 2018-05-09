from __future__ import unicode_literals

from django.db import models
from django.db.models.aggregates import Max


class SiteRegistrationQuerySet(models.QuerySet):
    def with_sensors(self):
        return self.prefetch_related('sensors')

    def deployed_by(self, user_id):
        return self.filter(django_user_id=user_id)

    def followed_by(self, user_id):
        return self.filter(followed_by__id=user_id)

    def with_latest_measurement(self):
        return self.annotate(latest_measurement=Max('sensors__last_measurement__value_datetime'))


class SiteSensorQuerySet(models.QuerySet):
    pass


class SensorOutputQuerySet(models.QuerySet):
    pass
