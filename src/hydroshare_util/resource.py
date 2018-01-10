import logging as logger

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
    def __init__(self, client, resource_id=None, creator=None, title="", abstract="", keywords=list(),
                 funding_agency=None, agency_url=None, award_title="", award_number=None, files=list(), subjects=list(),
                 period_start=None, period_end=None, public=False, resource_map_url=None, resource_url=None,
                 date_created=None, date_last_updated=None, discoverable=None, published=None, resource_type=None,
                 immutable=None, science_metadata_url=None, bag_url=None, coverages=None, shareable=None, **kwargs):

        self.client = client # type: HydroShareAdapter
        self.resource_id = resource_id
        self.title = self.resource_title = title
        self.abstract = abstract
        self.keywords = keywords
        self.funding_agency = funding_agency
        self.agency_url = agency_url
        self.award_title = award_title
        self.award_number = award_number
        self.creator = creator
        self.files = files
        self.subjects = subjects
        self.period_start = period_start
        self.period_end = period_end
        self.date_last_updated = date_last_updated
        self.bag_url = bag_url
        self.science_metadata_url = science_metadata_url
        self.resource_map_url = resource_map_url
        self.immutable = immutable
        self.shareable = shareable
        self.discoverable = discoverable
        self.published = published
        self.date_created = date_created
        self.resource_url = resource_url
        self.public = public
        self.resource_type = resource_type

        if isinstance(public, str):
            self.public = True if public.lower() == 'true' else False
        else:
            self.public = bool(public)

        self.coverages = list()
        for coverage in coverages:
            if isinstance(coverage, dict):
                self.coverages.append(Coverage(coverage=coverage))

        self.__user_info = None

        for key, value in kwargs.iteritems():
            if key == 'public':
                if isinstance(value, str):
                    self.public = True if value.lower() == 'true' else False
                else:
                    self.public = bool(value)
            else:
                setattr(self, key, value)

    @property
    def user_info(self):
        if self.__user_info:
            return self.__user_info
        else:
            return self.client.get_user_info()

    @user_info.setter
    def user_info(self, value):
        self.__user_info = value

    def add_coverage(self, coverage):
        self.coverages.append(Coverage(coverage=coverage))

    def get_file_list(self):
        file_list = []
        try:
            file_list = list(self.client.get_resource_file_list(self.resource_id))
        except Exception as e:
            print e
        return file_list

    def get_resources(self):
        filtered_resources = {}

    def update_metadata(self):
        pass

    def get_file(self):
        pass

    def filter_resources(self):
        pass

    def upload_files(self):
        pass

    def delete_files(self):
        pass

    def get_coverage_period(self):
        pass

    def delete(self):
        pass

    def create(self):
        pass

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