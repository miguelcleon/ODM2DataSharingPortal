import logging
import os
from hs_restclient import HydroShareNotFound
from hydroshare_util.adapter import HydroShareAdapter
from . import HydroShareUtilityBaseClass
from coverage import Coverage


class Resource(HydroShareUtilityBaseClass):
    """
    {
        'resource_id': '318480bd6db94393ac59347802df9057',
        'coverages': [
            {
                'type': 'box',
                'value': {
                    'northlimit': 51.12216756422692,
                    'projection': 'WGS 84 EPSG:4326',
                    'units': 'Decimal degrees',
                    'southlimit': 48.433992380251986,
                    'eastlimit': 18.894746595269186,
                    'westlimit': 11.833382262850698
                }
            }
        ],
        'date_last_updated': '12-08-2016',
        # 'bag_url': 'http://www.hydroshare.org/django_irods/download/bags/318480bd6db94393ac59347802df9057.zip',
        'science_metadata_url': 'http://www.hydroshare.org/hsapi/resource/318480bd6db94393ac59347802df9057/scimeta/',
        'creator': 'Jiri Kadlec',
        'resource_map_url': 'http://www.hydroshare.org/hsapi/resource/318480bd6db94393ac59347802df9057/map/',
        'immutable': False,
        'resource_title': 'Snow probability Czechia 2015-02-08',
        'shareable': True,
        'discoverable': True,
        'published': False,
        'date_created': '01-06-2016',
        'resource_url': 'http://www.hydroshare.org/resource/318480bd6db94393ac59347802df9057/',
        'public': True,
        'resource_type': 'RasterResource'
    }
    """
    def __init__(self, client, resource_id=None, creator=None, title="", abstract="", keywords=set(),
                 funding_agency=None, agency_url=None, award_title="", award_number=None, files=list(), subjects=list(),
                 period_start=None, period_end=None, public=False, resource_map_url=None, resource_url=None,
                 date_created=None, date_last_updated=None, discoverable=None, published=None, resource_type=None,
                 immutable=None, science_metadata_url=None, bag_url=None, coverages=None, shareable=None, **kwargs):

        self.client = client # type: HydroShareAdapter

        self.abstract = abstract
        self.award_number = award_number
        self.award_title = award_title
        self.agency_url = agency_url
        self.bag_url = bag_url
        self.creator = self.owner = creator
        self.date_created = date_created
        self.date_last_updated = date_last_updated
        self.discoverable = discoverable
        self.files = files
        self.funding_agency = funding_agency
        self.immutable = immutable
        self.keywords = keywords
        self.period_end = period_end
        self.period_start = period_start
        self.public = True if isinstance(public, str) and public.lower() == 'true' else bool(public)
        self.published = published
        self.resource_id = resource_id
        self.resource_map_url = resource_map_url
        self.resource_title = self.title = title
        self.resource_type = resource_type
        self.resource_url = resource_url
        self.science_metadata_url = science_metadata_url
        self.shareable = shareable
        self.subjects = subjects

        if isinstance(public, str):
            self.public = True if public.lower() == 'true' else False
        else:
            self.public = bool(public)

        self.coverages = list()
        for coverage in coverages:
            if isinstance(coverage, dict):
                self.coverages.append(Coverage(coverage=coverage))

        self._resource_types = [type for type in self._initialize_resource_types()]

        for key, value in kwargs.iteritems():
            if key == 'public':
                if isinstance(value, str):
                    self.public = True if value.lower() == 'true' else False
                else:
                    self.public = bool(value)
            else:
                setattr(self, key, value)

    def _initialize_resource_types(self):
        return self.client.get_resource_types()

    def add_coverage(self, coverage):
        self.coverages.append(Coverage(coverage=coverage))

    def get_file_list(self):
        try:
            return list(self.client.get_resource_file_list(self.resource_id))
        except Exception as e:
            print e
        return []

    def update_metadata(self, data=None):
        if data is None:
            data = self.get_metadata()
        return self.client.update_science_metadata(self.resource_id, data)

    def get_file(self):
        pass

    def filter_resources(self):
        pass

    def upload_files(self):
        try:
            for file in self.files:
                try:
                    self.client.deleteResourceFile(self.resource_id, os.path.basename(file))
                except HydroShareNotFound:
                    pass

                if not isinstance(file, str):
                    file = str(file)

                self.client.addResourceFile(self.resource_id, file)
                logging.info("File {} uploaded to remote {}".format(os.path.basename(file), self.resource_id))
        except Exception as e:
            logging.warn("Upload failed - could not complete upload to HydroShare due to exception: {}".format(e))
            return False
        except KeyError as e:
            logging.warn('Incorrectly formatted arguments given. Expected key not found: {}'.format(e))
            return False
        return True

    def delete_files(self, files=None):
        try:
            if files is None:
                files = self.get_file_list()
        except Exception as e:
            logging.warn("Failed to get file list for resource: {id}\n{e}".format(id=self.resource_id, e=e))
            return

        try:
            for file_info in files:
                url = file_info['url']
                logging.info("Deleting resource file: {file}".format(file=os.path.basename(url)))
                self.client.delete_resource_file(self.resource_id, os.path.basename(url))
        except Exception as e:
            logging.warn("Failed to delete files in resource {id}\n{e}".format(id=self.resource_id, e=e))


    def get_coverage_period(self):
        pass

    def delete(self):
        try:
            logging.info("Deleting resource: {id}".format(id=self.resource_id))
            self.client.delete_resource(self.resource_id)
        except Exception as e:
            logging.warn("Failed to delete resource {id}\n{e}".format(id=self.resource_id, e=e))

    def create(self):
        resource_id = self.client.create_resource(resource_type=self.resource_type, title=self.title,
                                                  abstract=self.abstract)
        return resource_id

    def update(self):
        pass

    def get_metadata(self):
        return {
            'title': self.title,
            'description': self.abstract,
            'funding_agencies': [{'agency_name': self.funding_agency,
                                  'award_title': self.award_title,
                                  'award_number': self.award_number,
                                  'agency_url': self.agency_url}],
            "coverage": [{"type": "period",
                          "value": {"start": self.period_start,
                                    "end": self.period_end}}]
        }

    def to_dict(self):
        data = {
            'abstract': self.abstract,
            'agency_url': self.agency_url,
            'award_title': self.award_title,
            'award_number': self.award_number,
            'bag_url': self.bag_url,
            'creator': self.creator,
            'date_created': self.date_created,
            'date_last_updated': self.date_last_updated,
            'discoverable': self.discoverable,
            'files': self.files,
            'funding_agency': self.funding_agency,
            'immutable': self.immutable,
            'keywords': self.keywords,
            'period_end': self.period_end,
            'period_start': self.period_start,
            'public': self.public,
            'published': self.published,
            'resource_id': self.resource_id,
            'resource_map_url': self.resource_map_url,
            'resource_title': self.resource_title,
            'resource_type': self.resource_type,
            'resource_url': self.resource_url,
            'science_metadata_url': self.science_metadata_url,
            'shareable': self.shareable,
            'subjects': self.subjects
        }

    def __str__(self):
        return '{title} with {lenfiles} files'.format(title=self.title, lenfiles=len(self.files))

    def __repr__(self):
        return "<{classname}: {title}>".format(classname=self.classname, title=self.title)


# class ResourceTemplate(ResourceBaseClass):
#     def __init__(self, template_name, title="", abstract="", keywords=list(), funding_agency=None, agency_url=None,
#                  award_title="", award_number=None):
#         super(ResourceTemplate, self).__init__(title=title, abstract=abstract, keywords=keywords,
#                                                funding_agency=funding_agency, agency_url=agency_url,
#                                                award_title=award_title, award_number=award_number)
#         self.template_name = template_name
#
#     def get_metadata(self):
#         template = self.get_metadata()
#         return {'funding_agencies': {'agency_name': template['funding_agency'],
#                                      'award_title': template['award_title'],
#                                      'award_number': template['award_number'],
#                                      'agency_url': template['agency_url']}}
#
#     def __str__(self):
#         return self.template_name
#
#     def __repr__(self):
#         return "<{classname}: {template_name}".format(classname=self.classname, template_name=self.template_name)


# __all__ = ["ResourceTemplate", "Resource"]
__all__ = ["Resource"]