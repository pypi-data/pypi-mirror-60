"""
Select widget for MonthField. Copied and modified from
https://docs.djangoproject.com/en/1.8/ref/forms/widgets/#base-widget-classes
"""
import datetime
from datetime import date

from django.forms import widgets
from django.utils.dates import MONTHS
from .util import string_type


def calc_years():
    now = datetime.datetime.now()
    this_year = now.year
    year_span = range(2015, this_year + 2)
    _years = list(zip(year_span, year_span))
    return _years


years = calc_years()


class MonthSelectorWidget(widgets.MultiWidget):
    class Media:
        css = {
            'screen': ('month/field/widget_month.css',)
        }

    def __init__(self, attrs=None):
        # create choices for days, months, years
        _widgets = list()
        _attrs = attrs or {}  # default class
        _attrs['class'] = (_attrs.get('class', '') + ' w-month-year').strip()
        _widgets.append(widgets.Select(attrs=_attrs, choices=MONTHS.items()))
        _attrs['class'] += " w-year"
        _widgets.insert(0, widgets.Select(attrs=_attrs, choices=years))

        super(MonthSelectorWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            if isinstance(value, string_type):
                m = int(value[5:7])
                y = int(value[:4])
                return [y, m]
            return [value.year, value.month]
        return [None, None]

    def format_output(self, rendered_widgets):
        return ''.join(rendered_widgets)

    def value_from_datadict(self, data, files, name):
        datelist = [
            widget.value_from_datadict(data, files, name + '_%s' % i)
            for i, widget in enumerate(self.widgets)]
        try:
            D = date(day=1, month=int(datelist[1]),
                     year=int(datelist[0]))
        except ValueError:
            return ''
        else:
            return str(D)
