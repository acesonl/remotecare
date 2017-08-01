# -*- coding: utf-8 -*-
"""
This module contains all the quality of healthcare (QOHC)
questionnaire models

:subtitle:`Class definitions:`
"""
from django.db import models
from django.utils.translation import ugettext as _
from apps.questionnaire.models import QuestionnaireBase

DEFAULT_TEN_SCORE = (
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


QOHC_DEFAULT_SCORE = (
    ('not_at_all', _('Nee, totaal niet')),
    ('a_bit', _('Een beetje')),
    ('largely', _('Grotendeels')),
    ('yes_very', _('Ja, zeer')),
)

QOHC_FILL_IN_SCORE = (
    ('yes', _('Ja, ik vul het in')),
    ('no', _('Nee, ik vul het nu niet in')),
)


# Quality of Health Care Questionnaire
class QOHCQuestionnaire(QuestionnaireBase):
    """
    Quality of health care questionnaire
    """
    # health care satisfaction score
    not_fill_in = models.CharField(
        choices=QOHC_FILL_IN_SCORE,
        max_length=32,
        verbose_name=_(
            'Wilt u de vragen over kwaliteit van de zorg invullen?'))

    hc_satisfaction_score = models.IntegerField(
        null=True,
        blank=True,
        choices=DEFAULT_TEN_SCORE,
        verbose_name=_('Hoe tevreden bent u over onze totale zorg voor u?'))

    serious_score = models.CharField(
        null=True,
        blank=True,
        choices=QOHC_DEFAULT_SCORE,
        max_length=32,
        verbose_name=_('Voelt u zich serieus genomen?'))
    friendly_score = models.CharField(
        null=True,
        blank=True,
        choices=QOHC_DEFAULT_SCORE,
        max_length=32,
        verbose_name=_('Voelt u zich vriendelijk en netjes behandeld?'))
    information_score = models.CharField(
        null=True,
        blank=True,
        choices=QOHC_DEFAULT_SCORE,
        max_length=32,
        verbose_name=_('Is de informatie die u krijgt over' +
                       ' uw ziekte goed begrijpelijk?'))

    # remote care satisfaction score
    rc_satisfation_score = models.IntegerField(
        null=True,
        blank=True,
        choices=DEFAULT_TEN_SCORE,
        verbose_name=_('Hoe tevreden bent u over de App Remote Care?'))

    # display name
    display_name = _('Kwaliteit van zorg')

    lower_case_name = 'qohcquestionnaire'

    @property
    def graphic_score_display(self):
        """
        Returns:
            The graphic score display to use for the graphic
        """
        # count of left/right pain scores
        count = self.hc_satisfaction_score

        if count is None:
            count = 0

        return count

    @property
    def graphic_score_max(self):
        return 10

    @property
    def graphic_score_min(self):
        return 1

    @property
    def graphic_score_name(self):
        return _('Kwaliteit zorg')

    @property
    def display_template(self):
        """
        Returns:
            The template path & name to be used for showing the details
            page for the filled in data for this questionnaire.
        """
        return 'questionnaire/details/QOHCQuestionnaire.html'
