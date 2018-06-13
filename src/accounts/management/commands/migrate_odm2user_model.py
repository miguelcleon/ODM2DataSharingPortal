from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        user_model = get_user_model()
        users = user_model.objects.filter(odm2user__isnull=False)
        for user in users:
            if user.odm2user.hydroshare_account:
                user.odm2user.hydroshare_account.user = user
                user.odm2user.hydroshare_account.save(update_fields=['user'])

            affiliation = user.odm2user.affiliation
            user_model.objects.filter(id=user.id).update(
                affiliation_id=affiliation.affiliation_id,
                organization_code=affiliation.organization and affiliation.organization.organization_code,
                organization_name = affiliation.organization and affiliation.organization.organization_name
            )
