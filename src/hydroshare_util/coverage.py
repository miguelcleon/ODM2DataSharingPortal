# coverage.py
from abc import ABCMeta, abstractmethod


class CoverageImplementor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def to_dict(self):
        pass


class Coverage(object):
    def __init__(self, coverage=None, implementation=None):
        if implementation:
            self.__implementation = implementation
        elif coverage:
            type = str(coverage['type'])
            if type.lower() == 'box':
                self.__implementation = BoxCoverage(**coverage)
            elif type.lower() == 'point':
                self.__implementation = PointCoverage(**coverage)
            else:
                self.__implementation = BaseCoverageClass(**coverage)
        else:
            self.__implementation = BaseCoverageClass()

    @property
    def type(self):
        return self.__implementation.type

    def to_dict(self):
        return self.__implementation.to_dict()


class BaseCoverageClass(CoverageImplementor):
    def __init__(self, **kwargs):
        self.type = None
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

    def to_dict(self):
        type = self.type if self.type else ''
        value = {}
        for attr in self.__dict__:
            value[attr] = self.__dict__[attr]
        return {
            'type': type,
            'value': value
        }


class BoxCoverage(BaseCoverageClass):
    def __init__(self, northlimit=None, eastlimit=None, southlimit=None, westlimit=None, projection=None, units=None,
                 **kwargs):
        super(BoxCoverage, self).__init__(**kwargs)
        self.northlimit = northlimit
        self.eastlimit = eastlimit
        self.southlimit = southlimit
        self.westlimit = westlimit
        self.projection = projection
        self.units = units


class PointCoverage(BaseCoverageClass):
    def __init__(self, name=None, north=None, east=None, projection=None, units=None, **kwargs):
        super(PointCoverage, self).__init__(**kwargs)
        self.type = 'point'
        self.name = name
        self.north = north
        self.east = east
        self.projection = projection
        self.units = units

    def to_dict(self):
        return {
            'type': self.type,
            'value': {
                'north': self.north,
                'east': self.east,
                'projection': self.projection,
                'units': self.units
            }
        }
