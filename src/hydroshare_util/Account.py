from . import _HydroShareUtilityBaseClass, HSUClassAttributeError


class HSUAccount(_HydroShareUtilityBaseClass):
    def __init__(self, id=None, email=None, first_name=None, last_name=None,
                 organization=None, username=None, **kwargs):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.organization = organization
        self.username = username

        for key, value in kwargs.iteritems():
            if key in self.__dict__:
                setattr(self, key, value)
            else:
                raise HSUClassAttributeError(self, key)

    def to_dict(self):
        account = self.get_metadata()
        return {
            'id': account['id'],
            'email': account['email'],
            'first_name': account['first_name'],
            'last_name': account['last_name'],
            'organization': account['organization'],
            'username': account['username']
        }

    def __repr__(self):
        return "<{classname}: {username}>".format(classname=type(self).__name__, username=self.username)


__all__ = ["HSUAccount"]
