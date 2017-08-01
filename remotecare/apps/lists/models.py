# -*- coding: utf-8 -*-
"""
This module contains the Hospital model definition.
All users are hospital 'bound' meaning that an healhtprofessional can only
search patients within his/hers hospital.

:subtitle:`Class definitions:`
"""
from django.db import models
from django.conf import settings


class Hospital(models.Model):
    '''
    Stores a list of hospitals
    '''
    abbreviation = models.CharField(max_length=20)
    full_name = models.CharField(max_length=255)
    city = models.CharField(max_length=128, blank=True, null=True)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    tags = models.TextField()

    @classmethod
    def json_add_url(cls):  # pragma: no cover
        '''
        Function which returns a json_url for this object
        '''
        return ''

    @classmethod
    def search_keys(cls):  # pragma: no cover
        '''
        Function which returns the search keys for this object
        '''
        return ('abbreviation', 'full_name')

    @classmethod
    def icon_url(cls):  # pragma: no cover
        '''
        Function which returns the icon to be used for this object
        '''
        return settings.STATIC_URL + 'images/lists/hospital.png'

    def __unicode__(self):
        '''
        Function which returns a string representation of the object
        '''
        return self.full_name

    class Meta:
        '''
        Meta class used for orderning of multiple objects
        '''
        ordering = ('abbreviation',)
