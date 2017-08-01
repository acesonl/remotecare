# -*- coding: utf-8 -*-
"""
This module contains all the quality of life (QOL)
questionnaire models

:subtitle:`Class definitions:`
"""
from django.db import models
from django.utils.translation import ugettext as _
from apps.questionnaire.models import QuestionnaireBase
from apps.questionnaire.default.models import StartQuestionnaire
from core.models import ManyToManyField

QOL_TEN_SCORE = (
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

QOL_YES_NO_CHOICES = (
    ('yes', _('Ja')),
    ('no', _('Nee')),
)

QOL_YES_NO_MAYBE_CHOICES = (
    ('yes', _('Ja')),
    ('no', _('Nee')),
    ('maybe', _('Misschien')),
)

QOL_FILL_IN_CHOICES = (
    ('yes', _('Ik vul het in')),
    ('no', _('Dit vul ik liever niet in')),
)


class QOLPracticalProblem(models.Model):
    """
    Stores a list of QOL practical problems
    """
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name


class QOLSocialProblem(models.Model):
    """
    Stores a list of QOL social problems
    """
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name


class QOLEmotionalProblem(models.Model):
    """
    Stores a list of QOL emotional problems
    """
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name


class QOLSpiritualProblem(models.Model):
    """
    Stores a list of QOL spiritual problems
    """
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name


class QOLFysicalProblem(models.Model):
    """
    Stores a list of QOL fysicial problems
    """
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name


class QOLChronCUQuestionnaire(QuestionnaireBase):
    """
    QOL for Chron en Colitis Ulcerosa
    """
    # QOL for Chron en Colitis Ulcerosa
    # complaints = models.IntegerField(choices=QOL_TEN_SCORE,
    # max_length=32, verbose_name=_('Hoe veel last heeft u van problemen,
    # klachten of zorgen? Dit gaat zowel om de lichamelijke klachten die
    # u ondervindt van uw ziekte als emotionele,
    # sociale of praktische problemen.'))

    # Problems
    hasproblems = models.CharField(
        choices=QOL_FILL_IN_CHOICES,
        max_length=32,
        verbose_name=_(
            'Hieronder en in de volgende stappen kunt u aangeven of' +
            ' u last heeft van praktische, sociale, emotionele of' +
            ' spirituele problemen. Als u dit liever niet invult' +
            ' , kunt u dat hier aangeven.'))
    practical_problems = ManyToManyField(
        QOLPracticalProblem,
        blank=True,
        verbose_name=_('Praktische problemen'),
        related_name='practial_problems')
    social_problems = ManyToManyField(
        QOLSocialProblem,
        blank=True,
        verbose_name=_('Gezins-/sociale problemen'),
        related_name='social_problems')
    emotional_problems = ManyToManyField(
        QOLEmotionalProblem,
        blank=True,
        verbose_name=_('Emotionele problemen'),
        related_name='emotional_problems')
    spiritual_problems = ManyToManyField(
        QOLSpiritualProblem,
        blank=True,
        verbose_name=_('Religieuze/spirituele problemen'),
        related_name='spiritual_problems')
    other_problems = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Andere problemen'))

    # Contact
    need_contact = models.CharField(
        null=True,
        blank=True,
        choices=QOL_YES_NO_MAYBE_CHOICES,
        max_length=32,
        verbose_name=_(
            'Zou u over deze problemen met een deskundige willen' +
            ' praten? (bijvoorbeeld een psycholoog of een' +
            ' maatschappelijk werker)'))

    @property
    def display_template(self):
        """
        Returns:
            The template path & name to be used for showing the details
            page for the filled in data for this questionnaire.
        """
        return 'questionnaire/details/QOLChronCUQuestionnaire.html'

    # display name
    display_name = _('Kwaliteit van leven')

    lower_case_name = 'qol_chron_cu_questionnaire'

    @property
    def graphic_score_display(self):
        """
        Returns:
            The score to display in the graphic
        """
        # count of left/right pain scores
        # is problem_severity score of the StartQuestionnaire...

        questionnaire_request = self.request_step.questionnairerequest
        problem_severity = None

        try:
            startquestionnaire = StartQuestionnaire.objects.get(
                request_step__questionnairerequest=questionnaire_request)
            problem_severity =\
                startquestionnaire.get_problem_severity_display()
        except StartQuestionnaire.DoesNotExist:
            problem_severity = 0
        return problem_severity

    @property
    def graphic_score_max(self):
        return 10

    @property
    def graphic_score_min(self):
        return 0

    @property
    def graphic_score_name(self):
        return _('Problemen, klachten of zorgen')


class QOLQuestionnaire(QOLChronCUQuestionnaire):
    """
    QOL generic version (include fysical problems)
    """
    # fysical Problems
    fysical_problems = ManyToManyField(
        QOLFysicalProblem,
        blank=True,
        verbose_name=_('Lichamelijke problemen'),
        related_name='fysical_problems')

    @property
    def display_template(self):
        """
        Returns:
            The template path & name to be used for showing the details
            page for the filled in data for this questionnaire.
        """
        return 'questionnaire/details/QOLQuestionnaire.html'

    lower_case_name = 'qol_questionnaire'
