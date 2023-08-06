import re
import datetime
import calendar

from .mx_datetimedelta import DateTimeDelta
from .mx_relativedatetime import RelativeDateTime


class DateTimeType(datetime.datetime):
    def __lt__(self, other):
        try:
            return super(DateTimeType, self).__lt__(other)
        except TypeError:
            if isinstance(self, DateTime) and isinstance(other, DateTimeDelta):
                return True
            return self.__cmp__(other) < 0

    def __gt__(self, other):
        try:
            return other.__lt__(self)
        except AttributeError:
            return True

    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)

    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)

    def __int__(self):
        epoch = datetime.datetime.utcfromtimestamp(0)
        delta = self - epoch
        return int(delta.total_seconds())

    def __cmp__(self, other,
                cmp=cmp):  # pragma: no cover
        if isinstance(other, DateTime):
            cmpdate = cmp(self.absdate, other.absdate)
            if cmpdate == 0:
                return cmp(self.abstime, other.abstime)
            else:
                return cmpdate
        elif other is None:
            return 1
        elif isinstance(other, (str, unicode)):
            return -1
        elif isinstance(other, (float, int, long)):
            return 1
        return -1


month_offset = (
    (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365),
    (0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366),
)


class DateTime(DateTimeType):
    def __new__(cls, year=0, month=1, day=1, hour=0, minute=0,
                second=0, microsecond=0):
        year_or_const = year
        if isinstance(year_or_const, datetime.datetime):
            t = year_or_const
            return datetime.datetime.__new__(
                cls, t.year, t.month, t.day, t.hour, t.minute, t.second,
                t.microsecond
            )
        elif isinstance(year_or_const, datetime.date):
            t = year_or_const
            return datetime.datetime.__new__(cls, t.year, t.month, t.day)
        year = max(year_or_const, 1)
        return datetime.datetime.__new__(
            cls, year, month, day, hour, minute, second, microsecond
        )

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return self.__add__(DateTimeDelta(other))
        elif isinstance(other, RelativeDateTime):
            return other.datetime_add(self)
        return DateTime(super(DateTime, self).__add__(other))

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return self.__add__(DateTimeDelta(-other))
        elif isinstance(other, datetime.timedelta):
            return DateTime(super(DateTime, self).__sub__(other))
        elif isinstance(other, datetime.datetime):
            delta = super(DateTime, self).__sub__(other)
            return DateTimeDelta.__from_delta__(delta)
        raise TypeError('Dont know what to do with %s' % repr(other))

    def __copy__(self):
        return DateTime(
            self.year, self.month, self.day, self.hour, self.minute,
            self.second, self.microsecond
        )

    def __deepcopy__(self, memo):
        return self.__copy__()

    @property
    def date(self):
        # return super(DateTime, self).date()
        return self.strftime('%Y-%m-%d')

    @property
    def time(self):
        # return super(DateTime, self).time()
        return self.strftime('%H:%M:%S.%f')[:-4]

    @property
    def day_of_week(self):
        return self.weekday()

    @property
    def days_in_month(self):
        return calendar.monthrange(self.year, self.month)[1]

    @property
    def iso_week(self):
        return self.isocalendar()

    def tuple(self):
        return tuple(self.timetuple())

    def is_leap(self):
        y = self.year
        return (y % 4 == 0) and ((y % 100 != 0) or (y % 400 == 0))

    @property
    def abstime(self):
        return (self.hour * 3600 + self.minute * 60) + self.second

    @property
    def absdate(self):
        year = self.year - 1
        yearoffset = year * 365 + year / 4 - year / 100 + year / 400
        year = year + 1
        return (
            self.day +
            month_offset[self.is_leap()][self.month - 1] +
            yearoffset
        )

    @property
    def absdays(self):
        return self.absdate - 1 + self.abstime / 86400.0


class DateTimeFrom(object):
    FORMATS = [
        '%y%m%d',
        '%y%m%d %H',
        '%y%m%d %H:%M',
        '%y%m%d %H:%M:%S',
        '%Y%m%d',
        '%Y%m%d %H',
        '%Y%m%d %H:%M',
        '%Y%m%d %H:%M:%S',
        '%d.%m.%Y',
        '%d.%m.%Y %H',
        '%d.%m.%Y %H:%M',
        '%d.%m.%Y %H:%M:%S',
        '%Y-%m-%d',
        '%Y-%m-%d %H',
        '%Y-%m-%d %H:%M',
        '%Y-%m-%d %H:%M:%S',
        '%m/%d/%Y',
        '%m/%d/%Y %H',
        '%m/%d/%Y %H:%M',
        '%m/%d/%Y %H:%M:%S',
        '%m/%d/%Y %I %p',
        '%m/%d/%Y %I:%M %p',
        '%m/%d/%Y %I:%M:%S %p',
        '%H:%M:%S'
    ]

    TIME_STRING_F_RE = re.compile('\d{1,2}:\d{1,2}:\d{1,2}.\d{1,2}')

    def __new__(cls, *args, **kwargs):
        if args and kwargs:
            raise TypeError('Can only be called with args OR kwargs')
        if args:
            if len(args) == 1:
                if isinstance(args[0], (str, unicode)):
                    return DateTimeFrom.__fromstring(args[0])
                elif isinstance(args[0], (DateTime)):
                    return args[0]
                elif isinstance(args[0], (datetime.datetime)):
                    return DateTime(args[0])
                elif isinstance(args[0], datetime.time):
                    return DateTime(
                        datetime.datetime.combine(datetime.date.min, args[0])
                    )
                elif isinstance(args[0], datetime.date):
                    return DateTime(
                        datetime.datetime.combine(args[0], datetime.time.min)
                    )
                else:
                    return (
                        DateTime(datetime.date.min) +
                        RelativeDateTime(year=1970) +
                        DateTimeDelta(seconds=args[0])
                    )
            else:
                return DateTime(*args)
        else:
            return DateTime(**kwargs)

    @classmethod
    def __fromstring(cls, s, first_attempt=True):
        for f in DateTimeFrom.FORMATS:
            try:
                return DateTime.strptime(s, f)
            except ValueError:
                pass
        if first_attempt and cls.TIME_STRING_F_RE.match(s):
            return cls.__fromstring(s.split('.')[0], first_attempt=False)
        raise ValueError('"%s" does not match any format' % s)
