# -*- coding: utf-8 -*-
"""
This module contains the healthprofessional model definition.
The healthprofessional is coupled to a :class:`apps.account.models.User`
instance via the :class:`apps.healthperson.models.HealthPerson` baseclass.

Inheritance-diagram:

.. inheritance-diagram::\
    apps.healthperson.healthprofessional.models.HealthProfessional

:subtitle:`Class definitions:`
"""
from django.db import models
from django.utils.translation import ugettext as _
from apps.healthperson.models import HealthPerson
from core.models import DateField, ImageField, AuditBaseModel

FUNCTION_CHOICES = (
    ('specialist', _('Medisch specialist')),
    ('assistant', _('Arts-assistent')),
    ('specializednurse', _('Gespecialiseerd verpleegkundige')),
    ('nurse', _('Verpleegkundige')),
    ('dietician', _('Dietist')),

)

SPECIALISM_CHOICES = (
    ('gastro_liver_disease', _('Maag-darm-leverziekten')),
    ('rheumatology', _('Reumatologie')),
    ('surgery', _('Chirurgie')),
    ('internal_medicine', _('Interne geneeskunde')),
    ('orhopedie', _('Orhopedie')),
)

NOTIFICATION_CHOICES = (
    ('sms_and_email', _('Zowel per e-mail als per sms')),
    ('sms_only', _('Alleen per sms')),
    ('email_only', _('Alleen per e-mail')),
    ('to_secretary', _('Doorsturen naar')),
)

OUT_OF_OFFICE_CHOICES = (
    ('', _('-------')),
    ('yes', _('Ja')),
    ('no', _('Nee')),
)


class HealthProfessional(HealthPerson, AuditBaseModel):
    '''
    Stores specific information healthprofessional including
    photo, function, specialism and notifications and out of office
    settings.
    '''
    photo_location = ImageField(
        upload_to='upload',
        max_length=128,
        null=True,
        blank=True,
        verbose_name=_('Pasfoto'))
    function = models.CharField(
        choices=FUNCTION_CHOICES,
        max_length=128,
        verbose_name=_('Functie'))
    specialism = models.CharField(
        choices=SPECIALISM_CHOICES,
        max_length=128,
        verbose_name=_('Specialisme'))
    telephone = models.CharField(
        max_length=256,
        verbose_name=_('Telefoonnummer contact polikliniek'))

    # Notification settings
    urgent_control_notification = models.CharField(
        choices=NOTIFICATION_CHOICES,
        default='sms_and_email',
        max_length=32,
        verbose_name=_('Langer dan 3 dagen niet gereageerd' +
                       'op een urgente patient.')
    )
    from apps.healthperson.secretariat.models import Secretary
    urgent_control_secretary = models.ForeignKey(
        Secretary,
        null=True,
        blank=True,
        verbose_name=_('Secretariaat medewerker'))
    out_of_office_start = DateField(
        blank=True,
        null=True,
        future=True,
        verbose_name=_('Start datum afwezigheid'))
    out_of_office_end = DateField(
        blank=True,
        null=True,
        future=True,
        verbose_name=_('Eind datum afwezigheid'))
    out_of_office_replacement = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        verbose_name=_('Vervangende specialist tijdens afwezigheid'),
        related_name='replacement_set')

    @property
    def photo_height(self):
        return 200

    @property
    def photo_width(self):
        return 100

    @property
    def name(self):
        return _('Behandelaar')
