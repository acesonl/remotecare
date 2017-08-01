"""
Provides extra HTML Widget classes
"""
import datetime
import re
from django.forms.widgets import Widget
from django.utils.dates import MONTHS, MONTHS_AP, MONTHS_3
from django.conf import settings

__all__ = ('SelectDateWidget',)

RE_DATE = re.compile(r'(\d{4})-(\d\d?)-(\d\d?)$')


class SelectDateWidget(Widget):
    '''
    A Widget that splits date input into three <select> boxes.

    This also serves as an example of a Widget that has more than one HTML
    element and hence implements value_from_datadict.
    '''
    # none_value = (0, '---')
    # month_field = '%s_month'
    # day_field = '%s_day'
    # year_field = '%s_year'

    date_format = [('year', 'Y'), ('day', 'j'), ('month', 'F')]

    def __init__(self, attrs=None, years=None, format=None, required=True):
        if attrs is None:
            attrs = {}
        self.attrs = attrs
        self.values = {}
        self.format = self.parse_format(format)
        self.required = required
        # years is an optional list/tuple of years to use in
        # the "year" select box.
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = list(range(this_year, this_year + 10))
        super(SelectDateWidget, self).__init__(attrs)

    def id_for_label(self, id_):
        '''
        Returns:
            the label for this widget
        '''
        return '%s_month' % id_
    id_for_label = classmethod(id_for_label)

    def value_from_datadict(self, data, files, name):
        '''
        Returns:
            the values from the post data based
            associated with this widget
        '''
        y = data.get('%s_year' % name)
        m = data.get('%s_month' % name)
        d = data.get('%s_day' % name)
        if y == m == d == '-1':
            return None
        if y and m and d:
            return u'-'.join([y, m, d])
        return data.get(name, None)

    def parse_value(self, val):
        '''
        Returns:
            An dict with month, day, year based on val or an empty dict
        '''
        ret = {}
        if isinstance(val, datetime.date):
            ret['month'] = val.month
            ret['day'] = val.day
            ret['year'] = val.year
        else:
            try:
                l = list(map(int, val.split('-')))
            except (ValueError, AttributeError):
                l = (None, None, None)
            for i, k in [(0, 'year'), (1, 'month'), (2, 'day')]:
                try:
                    ret[k] = l[i]
                except IndexError:
                    ret[k] = None
        return ret

    def parse_format(self, fmt):
        '''
        Parse the given format `fmt` and set the format property.
        '''
        if fmt is None:
            fmt = settings.DATE_FORMAT
        ret = []
        for item in fmt:
            if item in ['d', 'D', 'j', 'L']:
                ret.append(('day', item,))
            elif item in ['n', 'm', 'F', 'b', 'M', 'N']:
                ret.append(('month', item,))
            elif item in ['y', 'Y']:
                ret.append(('year', item,))
        return ret

    def month_choices(self, fmt):
        '''
        Return list of choices (tuple (key, value)) for monthes select.
        '''
        if fmt == 'n':
            # month numbers without leading 0 (1 .. 12)
            return [(i, i) for i in range(1, 13)]
        elif fmt == 'm':
            # month numbers with leading 0 (01 .. 12)
            return [(i, '%02d' % i) for i in range(1, 13)]
        elif fmt in ['F', 'b', 'M', 'N']:
            if fmt == 'F':
                # full month names
                month_choices = list(MONTHS.items())
            elif fmt == 'b':
                # 3 first letters of month lowercase
                month_choices = [
                    (k, v.lower()) for (k, v) in
                    list(MONTHS_3.items())
                ]
            elif fmt == 'M':
                # 3 first letters of month
                month_choices = list(MONTHS_3.items())
            elif fmt == 'N':
                # abbrev of month names
                month_choices = list(MONTHS_AP.items())
            month_choices.sort()
            return month_choices
        return []

    def day_choices(self, fmt):
        '''
        Return list of choices (tuple (key, value)) for days select.
        '''
        if fmt == 'j':
            # day of month number without leading 0
            return [(i, i) for i in range(1, 32)]
        elif fmt == 'd':
            # day of month number with leading 0
            return [(i, '%02d' % i) for i in range(1, 32)]
        return []

    def year_choices(self, fmt):
        '''
        Return list of choices (tuple (key, value)) for years select.
        '''
        if fmt == 'Y':
            # years with 4 numbers
            return [(i, i) for i in self.years]
        elif fmt == 'y':
            # years with only the last 2 numbers
            return [(i, str(i)[-2:]) for i in self.years]
        return []
