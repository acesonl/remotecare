# -*- coding: utf-8 -*-
"""
This module contains all the default questionnaire models

:subtitle:`Class definitions:`
"""
from django import forms
from django.db import models
from django.utils.translation import ugettext as _
from apps.questionnaire.models import QuestionnaireBase
from core.models import DateField, ChoiceOtherField

START_TEN_SCORE = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
)

START_HOSPITAL_CHOICES = (
    ('no', _('Nee')),
    ('yes_urgent_care', _('Ja, op de spoedopvang')),
    ('yes_intestional_clinic',
        _('Ja, op de polikliniek Maag-darm-leverziekten')),
    ('yes_other_specialist', _('Ja, bij een andere medisch specialist')),
)

START_STATUS_CHOICES = (
    ('good', _('Goed')),
    ('less_good', _('Iets minder goed')),
    ('bad', _('Slecht')),
    ('really_bad', _('Erg slecht')),
    ('terrible', _('Afschuwelijk')),
)


class StartQuestionnaire(QuestionnaireBase):
    """
    The start/first questionnaire for a normal control
    """
    current_status = models.CharField(
        choices=START_STATUS_CHOICES,
        max_length=32,
        verbose_name=_('Hoe gaat het met u?'))
    problems = models.TextField(verbose_name=_(
        'Kunt u hieronder beschrijven hoe het met u gaat' +
        ' en waar u op dit moment het meeste last van heeft?'))
    problem_severity = models.IntegerField(
        choices=START_TEN_SCORE,
        verbose_name=_('Hoe veel last heeft u van problemen, ' +
                       'klachten of zorgen? Dit gaat zowel om de' +
                       ' lichamelijke klachten die u ondervindt van' +
                       ' uw ziekte als emotionele, sociale of praktische' +
                       ' problemen. (1=geen klachten of problemen,10=heel' +
                       ' veel klachten of problemen)'))
    hospital_visit = models.CharField(
        choices=START_HOSPITAL_CHOICES,
        max_length=32,
        verbose_name=_('Bent u sinds de vorige controle nog' +
                       ' in het ziekenhuis geweest?'))
    # display name
    display_name = _('Hoe gaat het met u?')

    lower_case_name = 'startquestionnaire'

    @property
    def display_template(self):
        """
        Returns:
            The template path & name to be used for showing the details
            page for the filled in data for this questionnaire.
        """
        return 'questionnaire/details/StartQuestionnare.html'

DEFAULT_SCORE = (
    (1, _('1')),
    (2, _('2')),
    (3, _('3')),
    (4, _('4')),
    (5, _('5')),
)

APPOINTMENT_PERIOD_CHOICES = (
    ('tomorrow', _('Morgen')),
    ('within_3_days', _('Binnen 3 dagen')),
    ('this_week', _('Deze week')),
)


class StartUrgentQuestionnaire(QuestionnaireBase):
    """
    The start/first questionnaire for a urgent control
    """
    appointment_period = models.CharField(
        choices=APPOINTMENT_PERIOD_CHOICES,
        max_length=32,
        verbose_name=_('Op welke termijn zou u deze afspraak willen?'))

    # display name
    display_name = _('Direct een afspraak')

    lower_case_name = 'starturgentquestionnaire'

    @property
    def display_template(self):
        """
        Returns:
            The template path & name to be used for showing the details
            page for the filled in data for this questionnaire.
        """
        return 'questionnaire/details/StartUrgentQuestionnare.html'

URGENT_PROBLEM_TEN_SCORE = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
)


class UrgentProblemQuestionnaire(QuestionnaireBase):
    """
    The second part for the urgent control procedure.
    """
    problems = models.TextField(verbose_name=_(
        'Kunt u hieronder beschrijven hoe het met u gaat en waar' +
        ' u op dit moment het meeste last van heeft?'))
    problem_severity = models.IntegerField(
        choices=URGENT_PROBLEM_TEN_SCORE,
        verbose_name=_(
            'Hoe veel last heeft u van problemen, klachten of zorgen?' +
            ' Dit gaat zowel om de lichamelijke klachten die u ondervindt' +
            ' van uw ziekte als emotionele, sociale of praktische' +
            ' problemen. (1=geen klachten of problemen,10=heel' +
            ' veel klachten of problemen)'))

    display_name = _('Omschrijving problemen')

    lower_case_name = 'urgentproblemquestionnaire'

    @property
    def display_template(self):
        """
        Returns:
            The template path & name to be used for showing the details
            page for the filled in data for this questionnaire.
        """
        return 'questionnaire/details/UrgentProblemQuestionnaire.html'

APPOINTMENT_CHOICES = (
    ('no', _('Nee, dat hoeft niet')),
    ('yes_phone_nurse', _(
        'Ja, graag een telefonische afspraak met' +
        ' de gespecialiseerd verpleegkundige')),
    ('yes_phone_doctor', _(
        'Ja, graag een telefonisch afspraak met de arts')),
    ('yes_nurse', _(
        'Ja, graag een afspraak op de polikliniek met de' +
        ' gespecialiseerd verpleegkundige')),
    ('yes_doctor', _('Ja, graag een afspraak op de polikliniek met de arts')),
)

APPOINTMENT_PERIOD_CHOICES = (
    ('within_4_weeks', _('Binnen 4 weken')),
    ('within_2_weeks', _('Binnen 2 weken')),
    ('this_week', _('Deze week')),
)

APPOINTMENT_PREFERENCE = (
    ('None', _('Maakt niet uit')),
    ('other', _('Ja, dat wil ik graag aangegeven')),
)


BLOOD_SAMPLE_CHOICES = (
    ('umcg', _('UMCG')),
    ('martini_ziekenhuis', _('Martini Ziekenhuis')),
    ('lab_noord', _('Lab Noord')),
    ('other', _('Anders')),
)


class FinishQuestionnaire(QuestionnaireBase):
    """
    Finish/last questionnaire for the normal control
    """
    # Appointment
    appointment = models.CharField(
        choices=APPOINTMENT_CHOICES,
        max_length=32,
        verbose_name=_(
            'Wilt u, naast deze digitale conrole, graag een afspraak?'))
    appointment_period = models.CharField(
        blank=True,
        null=True,
        choices=APPOINTMENT_PERIOD_CHOICES,
        max_length=32,
        verbose_name=_('Op welke termijn zou u deze afspraak willen?'))
    appointment_preference = ChoiceOtherField(
        blank=True,
        null=True,
        choices=APPOINTMENT_PREFERENCE,
        max_length=512,
        verbose_name=_('Heeft u voorkeur voor een dag, periode of tijdstip?'),
        other_field=forms.Textarea)
    # blood samples
    blood_sample = ChoiceOtherField(
        choices=BLOOD_SAMPLE_CHOICES,
        max_length=128,
        verbose_name=_('Waar heeft u bloed laten prikken?'),
        help_text=_(
            'Indien u dit nog niet heeft gedaan, wilt u dan de' +
            ' controle opslaan en pas afronden nadat u bloed heeft geprikt?'))

# (bij afspraken). Aan het begin: Let op: voor deze controle moet u
# bloed laten prikken, voordat u de vragenlijst kan invullen en versturen.

    blood_sample_date = DateField(
        blank=True,
        null=True,
        allow_future_date=False,
        verbose_name=_('Wanneer heeft u bloed laten prikken?'))

    # display name
    display_name = _('Afspraken, Bloedprikken')
    lower_case_name = 'finishquestionnaire'

    @property
    def display_template(self):
        """
        Returns:
            The template path & name to be used for showing the details
            page for the filled in data for this questionnaire.
        """
        return 'questionnaire/details/FinishQuestionnaire.html'
