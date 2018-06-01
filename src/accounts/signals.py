from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from dataloader.models import People, Organization, Affiliation


@receiver(post_save, sender=get_user_model())
def handle_odm2_user_creation(sender, instance, created, update_fields, **kwargs):
    if created:
        organization = Organization.objects.filter(organization_code=instance.organization_code).first()
        person = People.objects.create(person_first_name=instance.first_name, person_last_name=instance.last_name)
        affiliation = Affiliation.objects.create(
            person=person,
            organization=organization,
            affiliation_start_date=datetime.utcnow(),
            primary_email=instance.email
        )

        instance.affiliation_id = affiliation.affiliation_id
        instance.organization_name = organization and organization.organization_name
        instance.save(update_fields=['affiliation_id', 'organization_name'])
    else:
        update_fields = update_fields or []
        fields_for_odm2 = ['first_name', 'last_name', 'email', 'organization_code']

        if any((True for field in update_fields if field in fields_for_odm2)):
            organization = Organization.objects.filter(organization_code=instance.organization_code).first()
            affiliation = instance.affiliation
            person = affiliation.person
            person.person_first_name = instance.first_name
            person.person_last_name = instance.last_name
            affiliation.primary_email = instance.email
            affiliation.organization = organization

            person.save()
            affiliation.save()
