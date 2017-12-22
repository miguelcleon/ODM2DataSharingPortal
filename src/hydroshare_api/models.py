from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

# Create your models here.
class HydroShareResource(models.Model):
    resource_id = models.UUIDField(primary_key=True, editable=True)
    resource_title = models.CharField(max_length=255)
    creator = models.CharField(max_length=255)
    resource_type = models.CharField(max_length=255)
    date_created = models.DateField()
    date_last_updated = models.DateField()
    public = models.BooleanField()
    shareable = models.BooleanField()
    discoverable = models.BooleanField()
    published = models.BooleanField()
    immutable = models.BooleanField()
    resource_url = models.URLField()
    bag_url = models.URLField()
    science_metadata_url = models.URLField()
    resource_map_url = models.URLField()

    def get_coverage(self):
        try:
            point_coverage = HydroSharePointCoverage.objects.get(resource=self.pk)
        except ObjectDoesNotExist:
            point_coverage = None

        try:
            box_coverage = HydroShareBoxCoverage.objects.get(resource=self.pk)
        except ObjectDoesNotExist:
            box_coverage = None

        if point_coverage and box_coverage:
            raise MultipleObjectsReturned('Resource has two coverage types assigned to it, but can only have one!')
        elif point_coverage:
            return point_coverage
        elif box_coverage:
            return box_coverage
        else:
            return None

    class Meta:
        db_table = 'hydroshare_resource'


class HydroSharePointCoverage(models.Model):
    resource = models.ForeignKey(HydroShareResource, db_column='resource_id')
    name = models.CharField(max_length=255)
    north = models.FloatField()
    east = models.FloatField()
    projection = models.CharField(max_length=255)
    units = models.CharField(max_length=255)

    class Meta:
        db_table = 'hydroshare_point_coverage'


class HydroShareBoxCoverage(models.Model):
    resource = models.ForeignKey(HydroShareResource, db_column='resource_id')
    northlimit = models.FloatField()
    eastlimit = models.FloatField()
    southlimit = models.FloatField()
    westlimit = models.FloatField()
    projection = models.CharField(max_length=255)
    units = models.CharField(max_length=255)

    class Meta:
        db_table = 'hydroshare_box_coverage'
