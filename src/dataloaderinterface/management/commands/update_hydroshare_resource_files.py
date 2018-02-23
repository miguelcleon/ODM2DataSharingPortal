from django.core.management.base import BaseCommand, CommandError
from dataloaderinterface.models import HydroShareResource
from dataloaderinterface.views import upload_hydroshare_resource_files
from hydroshare_util.resource import Resource
from hydroshare_util.auth import AuthUtil
from django.utils.termcolors import colorize
from django.utils import timezone
from datetime import datetime


class Command(BaseCommand):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('-f', '--force-update', action='store_true')

    def handle(self, force_update=False, *args, **options):
        resources = HydroShareResource.objects.all()

        upload_success_count = 0
        upload_fail_count = 0
        upload_skipped_count = 0
        self.stdout.write('\n' + str(datetime.now()) + colorize(' Starting Job: ', fg='blue') + 'Uploading site data to hydroshare')

        for resource in resources:

            if resource.hs_account is None:
                # If resource does not have hs_account, remove the resource.
                # This case should only happen to resources that have been disconnected
                # from the resource in HydroShare.
                resource.delete()
                continue

            # Skip resource if not pause_sharing
            if not resource.is_enabled:
                upload_skipped_count += 1
                continue

            # Skip if resource sync type is 'manual'
            if resource.sync_type.lower() == 'manual' and force_update is False:
                upload_skipped_count += 1
                continue

            # Skip resources that are not "due" for upload unless 'force_udpate' is True
            next_sync = resource.next_sync_date()
            now = timezone.now()
            diff = (now - next_sync).total_seconds()
            if diff < 0 and force_update is False:
                upload_skipped_count += 1
                continue

            site = resource.site_registration

            self.stdout.write(colorize('Uploading resource files for: ', fg='blue') + site.sampling_feature_code)

            try:
                # get auth token and upload files to resource
                auth = AuthUtil.authorize(token=resource.hs_account.token.to_dict())
                hs_resource = Resource(client=auth.get_client(), resource_id=resource.ext_id)
                upload_hydroshare_resource_files(site, hs_resource)

                upload_success_count += 1

                resource.last_sync_date = timezone.now()
                resource.save()

                self.stdout.write(colorize('\tSuccessfully uploaded file(s) for {0}'.format(site.sampling_feature_code), fg='blue'))

            except Exception as e:
                upload_fail_count += 1
                self.stderr.write(colorize('\nERROR: file upload failed, reason given:\n\t{0}'.format(e.message), fg='red'))

        self.stdout.write(colorize('\nJob finished uploading resource files to hydroshare.', fg='blue'))
        self.stdout.write(colorize('\t           Uploads successful: ', fg='blue') + str(upload_success_count))
        self.stdout.write(colorize('\t               Uploads failed: ', fg='blue') + str(upload_fail_count))
        self.stdout.write(colorize('\t            Resources skipped: ', fg='blue') + str(upload_skipped_count))
        self.stdout.write(colorize('\t                        Total: ', fg='blue') + str(len(resources)) + '\n')
