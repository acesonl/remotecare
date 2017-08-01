# -*- coding: utf-8 -*-
"""
Module with provides shortcuts
for datetime definitions

:subtitle:`Function definitions:`
"""
from django.conf import settings


def datetime_format(request):
    '''
    Custom datetime format definitions
    '''
    return {
        'DATE_FORMAT': settings.DATE_FORMAT,
        'TIME_FORMAT': settings.TIME_FORMAT,
        'DATETIME_FORMAT': settings.DATETIME_FORMAT,
        'SHORT_DATE_FORMAT': settings.SHORT_DATE_FORMAT,
        'DEBUG': settings.DEBUG
    }
