# -*- coding: utf-8 -*-
"""
This module contains the RCMessage model definition.

:subtitle:`Class definitions:`
"""
from django.db import models
from django.utils.translation import ugettext as _
from core.models import EncryptedTextField, EncryptedCharField, AuditBaseModel
from apps.healthperson.patient.models import Patient
from apps.healthperson.healthprofessional.models import HealthProfessional
from apps.healthperson.secretariat.models import Secretary
from django.utils.functional import cached_property
from apps.questionnaire.models import QuestionnaireRequest


class RCMessage(AuditBaseModel):
    '''
    Stores messages which can be sent from healthprofessional/secretary
    to patient with AES encryption

    .. note:: It's named RCMessage instead of just Message to avoid confusion
              with the Django build in Message
    '''
    # receiving patient
    patient = models.ForeignKey(Patient)

    # either a healthprofessional or a secretary has sent this message
    healthprofessional = models.ForeignKey(
        HealthProfessional, null=True, blank=True)
    secretary = models.ForeignKey(Secretary, null=True, blank=True)

    # Optional related questionnaire request
    related_to = models.ForeignKey(QuestionnaireRequest, null=True)

    # Subject, encrypted
    subject = EncryptedCharField(
        blank=False,
        max_length=265,
        null=False,
        verbose_name=_('Onderwerp'),
        encryption_key='encryption_key')

    # message, encrypted
    internal_message = EncryptedTextField(
        blank=True,
        null=True,
        encryption_key='encryption_key')

    # statuses
    added_on = models.DateField(auto_now_add=True)
    read_on = models.DateField(blank=True, null=True,)

    def message(self):
        """
        Shortcut to the internal_message field

        Returns:
            self.internal_message
        """
        return self.internal_message
    message.allow_tags = True

    @property
    def sender(self):
        """
        Shortcut to get the sender of the message

        Returns:
            self.healthprofessional or, if not set, self.secretary
        """
        if self.healthprofessional:
            return self.healthprofessional
        return self.secretary

    @property
    def audit_encryption_key_id(self):
        """
        Get the EncryptionKey id so it can be coupled to the log item
        in the audit.

        Returns:
            The id of the EncryptionKey that is used to encrypt the
            model instance.
        """
        patient = Patient.objects.select_related(
            'user').get(id=self.patient_id)
        return patient.user.personal_encryption_key_id

    @cached_property
    def encryption_key(self):
        # This makes getting the key faster
        from apps.account.models import EncryptionKey

        encrypted_key = EncryptionKey.get_with_healthperson_id(
            self.patient_id)
        return EncryptionKey(key=encrypted_key).key
