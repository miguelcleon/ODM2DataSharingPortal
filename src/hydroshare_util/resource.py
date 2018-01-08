import logging as logger

from . import HydroShareUtilityBaseClass
from utility import HydroShareUtility
from auth import AuthUtil

class ResourceBaseClass(HydroShareUtilityBaseClass):
    def __init__(self, **kwargs):
        self.title = ""
        self.abstract = ""
        self.keywords = list()
        self.funding_agency = None
        self.agency_url = ""
        self.award_title = ""
        self.award_number = None
        for key, value in kwargs.iteritems():
            setattr(self, key, value)


class Resource(ResourceBaseClass):
    def __init__(self, resource_id=None, utility=None, auth=None, owner=None, title="", abstract="", keywords=list(),
                 funding_agency=None, agency_url=None, award_title="", award_number=None, files=list(), subjects=list(),
                 period_start=None, period_end=None, public=False, **kwargs):
        super(Resource, self).__init__(title=title, abstract=abstract, keywords=keywords,
                                       funding_agency=funding_agency, agency_url=agency_url,
                                       award_title=award_title, award_number=award_number)
        self.resource_id = resource_id
        self.util = utility # type: HydroShareUtility
        self.auth = auth # type: AuthUtil
        self.owner = owner
        self.files = files
        self.subjects = subjects
        self.period_start = period_start
        self.period_end = period_end
        self.public = public


        self.__user_info__ = None

        for key, value in kwargs.iteritems():
            if key == 'resource_id':
                self.id = value
            elif key == 'creator':
                self.owner = value
            elif key == 'resource_title':
                self.title = value
            elif key == 'public':
                self.public = True
            else:
                setattr(self, key, value)

    @property
    def user_info(self):
        if self.__user_info__:
            return self.__user_info__
        else:
            return self.util.get_user_info()

    @user_info.setter
    def user_info(self, value):
        self.__user_info__ = value

    def get_file_list(self):
        file_list = []
        try:
            file_list = list(self.util.get_resource_file_list(self.resource_id))
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


class ResourceTemplate(ResourceBaseClass):
    def __init__(self, template_name, title="", abstract="", keywords=list(), funding_agency=None, agency_url=None,
                 award_title="", award_number=None):
        super(ResourceTemplate, self).__init__(title=title, abstract=abstract, keywords=keywords,
                                               funding_agency=funding_agency, agency_url=agency_url,
                                               award_title=award_title, award_number=award_number)
        self.template_name = template_name

    def get_metadata(self):
        template = self.get_metadata()
        return {'funding_agencies': {'agency_name': template['funding_agency'],
                                     'award_title': template['award_title'],
                                     'award_number': template['award_number'],
                                     'agency_url': template['agency_url']}}

    def __str__(self):
        return self.template_name

    def __repr__(self):
        return "<{classname}: {template_name}".format(classname=self.classname, template_name=self.template_name)


__all__ = ["ResourceTemplate", "Resource"]