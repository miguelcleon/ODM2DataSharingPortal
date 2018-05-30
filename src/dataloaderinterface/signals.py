from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_save
from django.dispatch.dispatcher import receiver

from dataloader.models import SamplingFeature, Site, Annotation, SamplingFeatureAnnotation, SpatialReference
from dataloaderinterface.models import SiteRegistration


@receiver(pre_save, sender=SiteRegistration)
def handle_site_registration_pre_save(sender, instance, update_fields=None, **kwargs):
    affiliation = instance.odm2_affiliation
    instance.django_user = get_user_model().objects.filter(affiliation_id=instance.affiliation_id).first()
    instance.person_id = affiliation.person_id
    instance.person_first_name = affiliation.person.person_first_name
    instance.person_last_name = affiliation.person.person_last_name
    instance.organization_id = affiliation.organization_id
    instance.organization_code = affiliation.organization and affiliation.organization.organization_code
    instance.organization_name = affiliation.organization and affiliation.organization.organization_name


@receiver(post_save, sender=SiteRegistration)
def handle_site_registration_post_save(sender, instance, created, update_fields=None, **kwargs):
    if created:
        sampling_feature = SamplingFeature.objects.create(
            sampling_feature_type_id='Site',
            sampling_feature_code=instance.sampling_feature_code,
            sampling_feature_name=instance.sampling_feature_name,
            elevation_m=instance.elevation_m,
            elevation_datum_id=instance.elevation_datum
        )

        Site.objects.create(
            sampling_feature=sampling_feature,
            site_type_id=instance.site_type,
            latitude=instance.latitude,
            longitude=instance.longitude,
            spatial_reference=SpatialReference.objects.get(srs_name='WGS84')
        )

        stream_name = Annotation(annotation_type_id='Sampling feature annotation', annotation_code='stream_name', annotation_text=instance.stream_name)
        major_watershed = Annotation(annotation_type_id='Sampling feature annotation', annotation_code='major_watershed', annotation_text=instance.major_watershed)
        sub_basin = Annotation(annotation_type_id='Sampling feature annotation', annotation_code='sub_basin', annotation_text=instance.sub_basin)
        closest_town = Annotation(annotation_type_id='Sampling feature annotation', annotation_code='closest_town', annotation_text=instance.closest_town)
        Annotation.objects.bulk_create([stream_name, major_watershed, sub_basin, closest_town])

        SamplingFeatureAnnotation.objects.bulk_create([
            SamplingFeatureAnnotation(annotation=stream_name, sampling_feature=sampling_feature),
            SamplingFeatureAnnotation(annotation=major_watershed, sampling_feature=sampling_feature),
            SamplingFeatureAnnotation(annotation=sub_basin, sampling_feature=sampling_feature),
            SamplingFeatureAnnotation(annotation=closest_town, sampling_feature=sampling_feature)
        ])

        # update site registration sampling_feature_id without triggering this signal again.
        SiteRegistration.objects\
            .filter(pk=instance.registration_id)\
            .update(sampling_feature_id=sampling_feature.sampling_feature_id)
    else:
        sampling_feature = instance.sampling_feature

        SamplingFeature.objects.filter(pk=instance.sampling_feature_id).update(
            sampling_feature_code=instance.sampling_feature_code,
            sampling_feature_name=instance.sampling_feature_name,
            elevation_m=instance.elevation_m,
            elevation_datum_id=instance.elevation_datum
        )

        Site.objects.filter(pk=instance.sampling_feature_id).update(
            site_type_id=instance.site_type,
            latitude=instance.latitude,
            longitude=instance.longitude
        )

        sampling_feature.annotations.filter(annotation_code='stream_name').update(annotation_text=instance.stream_name)
        sampling_feature.annotations.filter(annotation_code='major_watershed').update(annotation_text=instance.major_watershed)
        sampling_feature.annotations.filter(annotation_code='sub_basin').update(annotation_text=instance.sub_basin)
        sampling_feature.annotations.filter(annotation_code='closest_town').update(annotation_text=instance.closest_town)


