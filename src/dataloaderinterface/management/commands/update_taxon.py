from leafpack.models import Macroinvertebrate
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
import requests
import csv
import cStringIO
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):

        try:
            api_key = settings.GOOGLE_API_CONF['api_key']
            file_id = settings.GOOGLE_API_CONF['files']['taxon_spreadsheet']
        except KeyError:
            print("Update failed, you need to add 'google_api_conf' in settings.json. See the 'settings_template.json' example for help.")
            return

        url_base = 'https://www.googleapis.com/drive/v3/files/{file_id}/export?mimeType=text%2Fcsv&key={key}'

        request = requests.get(url_base.format(file_id=file_id, key=api_key))

        if request.status_code != 200:
            return

        data = request.content

        reader = csv.DictReader(cStringIO.StringIO(data), delimiter=',')

        for row in reader:
            taxon_name = row['TaxonName']
            common_name = row['CommonName']
            parent_name = row['Parent Taxon']
            itis_serial_num = row['ITIS Taxonomic Serial Number']
            url = row['URL']

            if not len(taxon_name):
                continue

            try:
                taxon = Macroinvertebrate.objects.get(scientific_name__iexact=taxon_name)
            except ObjectDoesNotExist:
                taxon = Macroinvertebrate()

            taxon.scientific_name = taxon_name
            taxon.common_name = common_name
            taxon.itis_serial_number = itis_serial_num
            taxon.url = url

            if len(parent_name):

                try:
                    parent = Macroinvertebrate.objects.get(scientific_name=parent_name)
                    taxon.family_of = parent
                except ObjectDoesNotExist:
                    continue

            taxon.save()






