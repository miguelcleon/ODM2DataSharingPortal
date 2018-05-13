from django.contrib.auth import get_user_model

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        user_model = get_user_model()
        users = user_model.objects.filter(odm2user__isnull=False)
        for user in users:
            affiliation = user.odm2user.affiliation
            user.affiliation_id = affiliation.affiliation_id
            user.hydroshare_account = user.odm2user.hydroshare_account
            user.organization_code = affiliation.organization and affiliation.organization.organization_code
            user.organization_name = affiliation.organization and affiliation.organization.organization_name
            user.save(update_fields=['affiliation_id', 'hydroshare_account', 'organization_code', 'organization_name'])
