import csv
import os
import re
from tempfile import mkstemp
from tempfile import mkstemp
from leafpack.models import LeafPack, LeafPackBug, LeafPackType, Macroinvertebrate
from dataloaderinterface.models import SiteRegistration
from uuid import UUID


class LeafPackCSVWRiter(object):
    DEFAULT_DASH_LENGTH = 20
    DEFAULT_CSV_DIALECT = csv.excel

    def __init__(self, leafpack, site):  # type: (LeafPack, SiteRegistration) -> None
        self.leafpack = leafpack
        self.site = site

        _, path = mkstemp(suffix='.csv')
        self.path = path
        self.writer = None

    def write(self):  # type: (csv.writer, LeafPack, SiteRegistration) -> None
        leafpack = self.leafpack
        site_registration = self.site

        with open(self.path, 'w') as fout:
            self.writer = csv.writer(fout, dialect=self.DEFAULT_CSV_DIALECT)

            data = self.get_data()

            # Write file header
            self.make_header(['Leaf Pack Experiment Details',
                              'These data were copied to HydroShare from the WikiWatershed Data Sharing Portal.'])

            self.blank_line()

            # write site registration information
            self.make_header(['Site Information',
                              'http://data.wikiwatershed.org/sites/SITE_CODE/{0}'.format(leafpack.uuid)])
            self.writer.writerow(['Site Code', site_registration.sampling_feature_code])
            self.writer.writerow(['Site Name', site_registration.sampling_feature_name])
            self.writer.writerow(['Site Description', site_registration.sampling_feature.sampling_feature_description])
            self.writer.writerow(['Latitude', site_registration.latitude])
            self.writer.writerow(['Longitude', site_registration.longitude])
            self.writer.writerow(['Elevation (m)', site_registration.elevation_m])
            self.writer.writerow(['Vertical Datum', site_registration.sampling_feature.elevation_datum])
            self.writer.writerow(['Site Type', site_registration.site_type])

            self.blank_line()

            # write leafpack data
            self.make_header(['Leaf Pack Details'])
            for key, value in data.iteritems():
                self.writer.writerow([key.title(), value])

            self.blank_line()

            # write taxon names and corresponding count
            self.make_header(['Macroinvertebrate Counts'])

            for lpg in LeafPackBug.objects.filter(leaf_pack=leafpack):
                if lpg.bug_count:
                    self.writer.writerow([lpg.bug.common_name.title(), lpg.bug_count])

            self.blank_line()

            # write water quality index values
            self.make_header(['Water Quality Index Values'])
            self.writer.writerow(['Total number of individuals found', str(leafpack.total_bug_count())])
            biotic_index = leafpack.biotic_index()
            self.writer.writerow(['Biotic Index', round(biotic_index, 2)])
            self.writer.writerow(['Water Quality Category', leafpack.water_quality(biotic_index=biotic_index)])
            self.writer.writerow(['Percent EPT', round(leafpack.percent_EPT(), 2)])

    def read(self):
        with open(self.path, 'rb') as fout:
            data = fout.read()
        return data

    def get_data(self):
        data = dict()
        ignored_fields = ('id', 'uuid')
        lp_fields = LeafPack._meta.get_fields()

        for field in lp_fields:
            field_value = None

            if field.is_relation and field.name == 'types':
                types = getattr(self.leafpack, field.name, None)

                if types is not None:
                    field_value = ', '.join([t.name for t in types.all()])

            elif field.is_relation:

                continue

            else:

                field_value = getattr(self.leafpack, field.name, None)

            if field_value is not None and field.name not in ignored_fields:
                if field.name == 'types':
                    field_name = 'Leaf Pack Types and Composition'
                else:
                    field_name = " ".join(field.name.split("_"))

                if 'leafpack' in field_name.lower():
                    field_name = re.sub('leafpack', 'Leaf Pack', field_name)

                data[field_name] = str(field_value)

        return data

    def make_header(self, rows):
        self.writer.writerow(rows)
        self.dash_line(len(rows[0]))

    def dash_line(self, dash_count=None):
        if dash_count is None:
            dash_count = self.DEFAULT_DASH_LENGTH
        self.writer.writerow(['-' * dash_count])

    def blank_line(self):
        self.writer.writerow([])








