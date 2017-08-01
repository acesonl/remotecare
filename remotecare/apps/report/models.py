# -*- coding: utf-8 -*-
"""
Module which defines the Report model.

:subtitle:`Class definitions:`
"""
from django.db import models
from django.utils.translation import ugettext as _
from core.models import EncryptedTextField, AuditBaseModel
from apps.healthperson.healthprofessional.models import HealthProfessional
from apps.questionnaire.models import QuestionnaireRequest


class Report(AuditBaseModel):
    '''
    Model for saving reports of filled in questionnaires.
    Standard templates are used to generate the report which
    can be edited by the healthprofessional.

    The report is encrypted with use of the personal key of
    the created_by healthprofessional
    '''
    questionnaire_request = models.ForeignKey(QuestionnaireRequest)
    created_by = models.ForeignKey(HealthProfessional)
    created_on = models.DateField(auto_now_add=True)
    finished_on = models.DateField(null=True, blank=True)

    # Report is invalid
    invalid = models.BooleanField(default=False)

    # Sent to doctor?
    sent_to_doctor = models.BooleanField(
        default=False,
        verbose_name=_('Na opslaan naar huisarts sturen'))

    # Healthprofessional thinks that patient needs appointment.
    patient_needs_appointment = models.BooleanField(
        default=False,
        verbose_name=_('Patient alsnog oproepen voor afspraak polikliniek'),
        help_text=_(
            'De patient heeft aangegeven zelf geen polikliniek' +
            ' afspraak nodig te vinden. Wilt u op basis van de antwoorden' +
            ' en eventuele laboratoriumuitslagen de patient alsnog oproepen?'))

    # Report that is saved with healthprofessional data key
    report = EncryptedTextField(
        help_text=_('Nb. selecteer eerst de optie(s) hierboven' +
                    ' voordat u de tekst wijzigt.'),
        encryption_key='encryption_key')

    @property
    def filled_in(self):  # pragma: no cover
        """
        Returns:
            True if finished_on is set
        """
        return self.finished_on is not None

    @property
    def audit_encryption_key_id(self):
        """
        Get the EncryptionKey id so it can be coupled to the log item
        in the audit.

        Returns:
            The id of the EncryptionKey that is used to encrypt the
            model instance.
        """
        created_by = HealthProfessional.objects.select_related(
            'user').get(id=self.created_by_id)
        return created_by.user.personal_encryption_key_id

    @property
    def encryption_key(self):
        # This makes getting the key faster
        from apps.account.models import EncryptionKey

        encrypted_key = EncryptionKey.get_with_healthperson_id(
            self.created_by_id)
        return EncryptionKey(key=encrypted_key).key
