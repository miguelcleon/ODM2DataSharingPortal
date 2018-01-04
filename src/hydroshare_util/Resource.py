from . import _HydroShareUtilityBaseClass


class HSUResourceBaseClass(_HydroShareUtilityBaseClass):
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


class HSUResourceTemplate(HSUResourceBaseClass):
    def __init__(self, template_name, title="", abstract="", keywords=list(), funding_agency=None, agency_url=None,
                 award_title="", award_number=None):
        super(HSUResourceTemplate, self).__init__(title=title, abstract=abstract, keywords=keywords,
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


class HSUResource(HSUResourceBaseClass):
    def __init__(self, id=None, owner=None, title="", abstract="",
                 keywords=list(), funding_agency=None, agency_url=None,
                 award_title="", award_number=None, files=list(),
                 subjects=list(), period_start=None, period_end=None,
                 public=False, **kwargs):
        super(HSUResource, self).__init__(title=title, abstract=abstract, keywords=keywords,
                                          funding_agency=funding_agency, agency_url=agency_url,
                                          award_title=award_title, award_number=award_number)
        self.id = id
        self.owner = owner
        self.files = files
        self.subjects = subjects
        self.period_start = period_start
        self.period_end = period_end
        self.public = public

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

    def __str__(self):
        return '{title} with {lenfiles} files'.format(title=self.title, lenfiles=len(self.files))

    def __repr__(self):
        return "<{classname}: {title}>".format(classname=self.classname, title=self.title)

    def get_metadata(self):
        resource = self.get_metadata()

        return {
            'title': resource['title'],
            'description': resource['abstract'],
            'funding_agencies': [{'agency_name': resource['funding_agency'],
                                  'award_title': resource['award_title'],
                                  'award_number': resource['award_number'],
                                  'agency_url': resource['agency_url']}],
            "coverage": [{"type": "period",
                          "value": {"start": resource['period_start'],
                                    "end": resource['period_end']}}]
        }

__all__ = ["HSUResourceTemplate", "HSUResource"]