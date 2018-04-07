# coverage.py
from abc import ABCMeta, abstractmethod


class CoverageImplementor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def to_dict(self):
        pass


class CoverageFactory(object):
    def __init__(self, coverage=None, implementation=None):
        if implementation:
            self.__implementation = implementation
        elif coverage:
            type_ = str(coverage['type'])
            if type_.lower() == 'box':
                self.__implementation = BoxCoverage(**coverage)
            elif type_.lower() == 'point':
                self.__implementation = PointCoverage(**coverage)
            else:
                self.__implementation = Coverage(**coverage)
        else:
            self.__implementation = Coverage()

    @property
    def type(self):
        return self.__implementation.type_

    def to_dict(self):
        return self.__implementation.to_dict()


class Coverage(CoverageImplementor):
    type_ = None

    def __init__(self, **kwargs):
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

    def to_dict(self):
        value = {}
        for attr in self.__dict__:
            value[attr] = self.__dict__[attr]
        return {
            'type': self.type_,
            'value': value
        }


class BoxCoverage(Coverage):
    """
    BoxCoverage (also known as spatial coverage) is a type of coverage that specifies a geographical area with North,
    East, South, and West limits.
    """
    type_ = 'box'

    def __init__(self, northlimit=None, eastlimit=None, southlimit=None, westlimit=None, projection=None, units=None,
                 **kwargs):
        super(BoxCoverage, self).__init__(**kwargs)
        self.northlimit = northlimit
        self.eastlimit = eastlimit
        self.southlimit = southlimit
        self.westlimit = westlimit
        self.projection = projection
        self.units = units

    def to_dict(self):
        return {
            'type': self.type_,
            'value': {
                'northlimit': self.northlimit,
                'eastlimit': self.eastlimit,
                'southlimit': self.southlimit,
                'westlimit': self.westlimit,
                'units': self.units,
                'projection': self.projection
            }
        }


class PointCoverage(Coverage):
    """PointCoverage is a type of coverage that specifies an exact geographical location."""
    type_ = 'point'

    DEFAULT_PROJECTION = "WGS 84 EPSG:4326"
    DEFAULT_UNITS = "Decimal degrees"

    def __init__(self, name=None, latitude=None, longitude=None, projection=None, units=None, **kwargs):
        super(PointCoverage, self).__init__(**kwargs)
        self.name = name.encode('ascii') if name is not None else None
        self.north = latitude
        self.east = longitude
        self.projection = projection.encode('ascii') if projection is not None else None
        self.units = units.encode('ascii') if units is not None else None

    def to_dict(self):
        return {
            'type': self.type_,
            'value': {
                'north': self.north if self.north is not None else "",
                'east': self.east if self.east is not None else "",
                'projection': self.projection if self.projection is not None else self.DEFAULT_PROJECTION,
                'units': self.units if self.units is not None else self.DEFAULT_UNITS,
                'name': self.name if self.name is not None else ""
            }
        }


class PeriodCoverage(Coverage):
    """
    PeriodCoverage (also known as temporal coverage) is a type of coverage that specifies a period of time over
    which data is collected.
    """
    type_ = 'period'

    def __init__(self, start=None, end=None, **kwargs):
        super(PeriodCoverage, self).__init__(**kwargs)
        self.start = start
        self.end = end

    def to_dict(self):
        return {
            'type': self.type_,
            'value': {
                'start': self.start,
                'end': self.end
            }
        }


__all__ = ["CoverageFactory", "Coverage", "BoxCoverage", "PointCoverage", "PeriodCoverage"]
