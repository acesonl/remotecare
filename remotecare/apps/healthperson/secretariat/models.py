# -*- coding: utf-8 -*-
"""
This module contains the secretary model definition.
The secretary is coupled to a :class:`apps.account.models.User`
instance via the :class:`apps.healthperson.models.HealthPerson` baseclass.

Inheritance-diagram:

.. inheritance-diagram::\
    apps.healthperson.secretariat.models.Secretary

:subtitle:`Class definitions:`
"""
from django.db import models
from django.utils.translation import ugettext as _
from apps.healthperson.models import HealthPerson
from core.models import AuditBaseModel


SPECIALISM_CHOICES = (
    ('gastro_liver_disease', ('Maag-darm-leverziekten')),
    ('rheumatology', ('Reumatologie')),
    ('surgery', ('Chirurgie')),
    ('internal_medicine', ('Interne geneeskunde')),
    ('orhopedie', ('Orhopedie')),
)


class Secretary(HealthPerson, AuditBaseModel):
    """
    Stores extra information for a secretary
    """
    specialism = models.CharField(
        choices=SPECIALISM_CHOICES,
        max_length=128,
        verbose_name=_('Specialisme'))

    @property
    def name(self):
        return _('Medewerker')
