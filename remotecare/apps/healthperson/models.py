# -*- coding: utf-8 -*-
"""
This module includes the definition for the HealthPerson model.

The polymorphic model :class:`HealthPerson` is used as a baseclass for the\
different models coupled to Remote Care roles:

.. inheritance-diagram:: apps.healthperson.management.models.Manager\
     apps.healthperson.secretariat.models.Secretary\
     apps.healthperson.patient.models.Patient\
     apps.healthperson.healthprofessional.models.HealthProfessional

The :class:`HealthPerson` is set as a "ForeignKey" on the
:class:`apps.account.models.User` user model. This allows every user
to have a different model corresponding to their role.

:subtitle:`Class definitions:`
"""

from django.db import models
from polymorphic.models import PolymorphicModel


class HealthPerson(PolymorphicModel):
    '''
    The healthperson is the polymorphic model baseclass for the\
    different user models in Remote Care:
        - Healthprofessional
        - manager
        - patient
        - secretary


    The :class:`HealthPerson` is set as a "ForeignKey" on the
    :class:`apps.account.models.User` user model. This allows every user
    to have a different model corresponding to their role.
    '''
    added_on = models.DateField(auto_now_add=True)
    added_by = models.ForeignKey("self", null=True, blank=True)

    @property
    def name(self):
        return self.polymorphic_ctype.name

    @property
    def health_person_id(self):
        """
        The health_person_id (=self.id) is not directly used in url's of
        healthperson's but is stored in the session with a random key instead.
        This random key is included in the url's and used in the views
        to get the id of the healthperson. This way the id's are completely
        invisible for users and makes it impossible to easy switch to data
        of another user.

        In an older version the HealhPerson had a seperate health_person_id
        field, this has been replaced with the 'id' field. In order to not
        have to change all the templates it has been added as a property.

        Returns:
            self.id
        """
        return self.id
