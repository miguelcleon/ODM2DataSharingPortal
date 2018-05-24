# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from dataloaderinterface.models import SiteRegistration
from accounts.models import User


class Macroinvertebrate(models.Model):
    """
    :var: scientific_name: The scientific name for the macroinvertebrate (i.e. 'Ephemeroptera')
    :var: common_name: The common for the macroinvertebrate (i.e. 'mayflies')
    :var: family_of: Establishes an Order-Family one-to-many relationships. For example, in biological classification,
     Diptera is the order of all true flies and includes the families of Anthericidae, Chironomidae, Simuliidae, etc.,
     but all are macroinvertebrate.
    """
    class Meta:
        db_table = 'macroinvertebrate'

    scientific_name = models.CharField(max_length=255, unique=True)
    common_name = models.CharField(max_length=255, unique=True)
    family_of = models.ForeignKey('Macroinvertebrate',
                                  on_delete=models.CASCADE,
                                  null=True,
                                  blank=True,
                                  related_name='families')
    pollution_tolerance = models.FloatField()

    """
    'sort_priority' is used to determine the order taxon appear on things like django forms. HIGHER values  
    of sort_priority should appear first, and LOWER values last
    """
    sort_priority = models.FloatField(default=0)

    @property
    def is_ept(self):
        return self.scientific_name.lower() in ['ephemeroptera', 'plecoptera', 'tricoptera']

    def __str__(self):
        return '{0} ({1})'.format(self.common_name.title(), self.scientific_name.title())

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.family_of is not None and len(self.families.all()):
            raise AttributeError("'{}' is a parent of another taxon and therefore cannot be a subcategory of '{}'".format(
                self.__str__(), self.family_of.__str__()
            ))

        if self.family_of and self.family_of.family_of is not None:
            raise AttributeError("'{}' is a subcategory of another taxon and therefore cannot be a parent of '{}'".format(
                self.family_of.__str__(), self.__str__()
            ))

        super(Macroinvertebrate, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                            update_fields=update_fields)


class LeafPack(models.Model):
    """
    Leaf pack data
    """
    class Meta:
        db_table = 'leafpack'

    site_registration = models.ForeignKey(SiteRegistration, on_delete=models.CASCADE)
    placement_date = models.DateField()
    retrieval_date = models.DateField()
    leafpack_placement_count = models.IntegerField()
    leafpack_retrieval_count = models.IntegerField()
    placement_air_temp = models.FloatField()
    placement_water_temp = models.FloatField()
    retrieval_air_temp = models.FloatField()
    retrieval_water_temp = models.FloatField()
    had_storm = models.BooleanField(default=False)
    had_flood = models.BooleanField(default=False)
    had_drought = models.BooleanField(default=False)
    storm_count = models.IntegerField(default=0)
    storm_precipitation = models.FloatField(default=0)
    types = models.ManyToManyField('LeafPackType')

    def total_bug_count(self):
        """
        Gets the total count of taxon for the entire leafpack experiement.
        The forumla is: Summation, from 1 to n taxon, of nth taxon count minus the summation of sub-category taxon count

        :var total: The total taxon count
        :var lpgs: LeafPackBugs associated with this LeafPack whose count is greater than zero
        :return: total taxon count.
        """
        total = 0
        lpgs = LeafPackBug.objects.filter(leaf_pack=self, bug_count__gt=0)

        for lpg in lpgs:
            sub_taxons = lpg.bug.families.all()
            sub_taxon_count = 0

            for taxon in sub_taxons:
                lpg_taxon = LeafPackBug.objects.get(leaf_pack=self, bug=taxon)
                sub_taxon_count += lpg_taxon.bug_count

            total += lpg.bug_count - sub_taxon_count

        return total

    def percent_EPT(self):
        """
        :return: The sum of the percentages of Ephemeroptera, Placoptera, and Tricoptera
        """
        total = self.total_bug_count()

        ephemeroptera = Macroinvertebrate.objects.get(scientific_name='Ephemeroptera')
        placoptera = Macroinvertebrate.objects.get(scientific_name='Plecoptera')
        tricoptera = Macroinvertebrate.objects.get(scientific_name='Tricoptera')

        ephemeroptera_count = LeafPackBug.objects.get(leaf_pack=self, bug=ephemeroptera).bug_count
        placoptera_count = LeafPackBug.objects.get(leaf_pack=self, bug=placoptera).bug_count
        tricoptera_count = LeafPackBug.objects.get(leaf_pack=self, bug=tricoptera).bug_count

        if total == 0:
            return 0

        return (float(ephemeroptera_count + placoptera_count + tricoptera_count) / float(total)) * 100.0

    def biotic_index(self):
        leafpack_count = self.leafpack_retrieval_count

        if leafpack_count == 0:
            return 0

        count_avg_total = tolerance_avg_total = 0

        lpgs = LeafPackBug.objects.filter(leaf_pack=self)

        for lpg in lpgs:
            sub_taxon_count = 0
            sub_taxons = lpg.bug.families.all()

            for sub_taxon in sub_taxons:
                sub_lpg = LeafPackBug.objects.get(leaf_pack=self, bug=sub_taxon)
                sub_taxon_count += sub_lpg.bug_count

            count_avg = float(lpg.bug_count - sub_taxon_count) / float(leafpack_count)
            count_avg_total += count_avg
            tolerance_avg_total += (count_avg * lpg.bug.pollution_tolerance)

        if count_avg_total == 0:
            return 0

        return float(tolerance_avg_total) / float(count_avg_total)

    def water_quality(self, biotic_index=None):
        if not biotic_index:
            biotic_index = self.biotic_index()

        if biotic_index < 3.75:
            return 'Excellent - Organic pollution unlikely'
        elif 3.75 <= biotic_index < 5.0:
            return 'Good - Some organic pollution'
        elif 5.0 <= biotic_index < 6.5:
            return 'Fair - Substantial pollution likely'
        else:
            return 'Poor - Severe pollution likely'


class LeafPackBug(models.Model):
    """
    This model defines the many-to-many relationship between LeafPack and Macroinvertebrate models
    :var: leaf_pack: An instance of LeafPack
    :var: bug: An instance of Macroinvertebrate... 'bug' is easier to spell...
    :var: bug_count: The number of associated macroinvertebrate counted in the associated leaf pack
    """
    class Meta:
        db_table = 'leafpack_bug'

    leaf_pack = models.ForeignKey(LeafPack, on_delete=models.CASCADE)
    bug = models.ForeignKey(Macroinvertebrate, on_delete=models.CASCADE)
    bug_count = models.IntegerField(default=0)


class LeafPackType(models.Model):
    """
    A simple class to store a leaf pack type (i.e. beech, birch, elm, gum, maple, pine, etc.)
    """
    class Meta:
        db_table = 'leafpack_type'

    name = models.CharField(max_length=255, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name
