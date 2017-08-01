# -*- coding: utf-8 -*-
"""
This module contains all the inflammatory bowel disease (IBD)
questionnaire models

:subtitle:`Class definitions:`
"""
from decimal import Decimal
from django.db import models
from django.utils.translation import ugettext as _
from apps.questionnaire.models import QuestionnaireBase
from core.models import ManyToManyField

IBD_STATUS_CHOICES = (
    ('good', _('Goed')),
    ('less_good', _('Iets minder goed')),
    ('bad', _('Slecht')),
    ('really_bad', _('Erg slecht')),
    ('terrible', _('Afschuwelijk')),
)

IBD_TEN_SCORE = (
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

IBD_HOSPITAL_CHOICES = (
    ('no', _('Nee')),
    ('yes_urgent_care', _('Ja, op de Spoedopvang')),
    ('yes_intestional_clinic',
        _('Ja, op de polikliniek Maag-darm-leverziekten')),
    ('yes_other_specialist', _('Ja, bij een andere medisch specialist')),
)


IBD_YES_NO_CHOICES = (
    ('yes', _('Ja')),
    ('no', _('Nee')),
)

IBD_YES_NO_UNKNOWN_CHOICES = (
    ('yes', _('Ja')),
    ('no', _('Nee')),
    ('dont_know', _('Weet ik niet')),
)
IBD_STOOL_FREQ_CHOICES = (
    ('1_3_times', _('1-3 maal')),
    ('4_6_times', _('4-6 maal')),
    ('7_9_times', _('7-9 maal')),
    ('more_than_9_times', _('Meer dan 9 maal')),
)

IBD_STOOL_THICKNESS_CHOICES = (
    ('hard', _('Hard')),
    ('normal', _('Normaal')),
    ('mushy', _('Brijig')),
    ('liquid', _('Vloeibaar of Waterdun')),
)

IBD_STOOL_LIQUID_CHOICES = (
    ('less_than_1_time_per_day', _('< 1 maal per dag')),
    ('1_2_times_per_day', _('1-2 maal per dag')),
    ('3_6_times_per_day', _('3-6 maal per dag')),
    ('more_than_6_times_per_day', _('Meer dan 6 maal per dag')),
)

IBD_STOOL_BLOOD_CHOICES = (
    ('no', _('Nee')),
    ('sometimes', _('Soms')),
    ('often_or_daily', _('Vaak of zelfs dagelijks')),
)

IBD_STOOL_SLIME_CHOICES = (
    ('no', _('Nee')),
    ('sometimes', _('Soms')),
    ('often_or_daily', _('Vaak of zelfs dagelijks')),
)

IBD_STOOL_URGENCY_CHOICES = (
    ('no', _('Nee')),
    ('yes_sometimes', _('Ja, soms')),
    ('yes_severe', _('Ja, ernstig')),
)

IBD_STOOL_PLANNING_CHOICES = (
    ('no_never', _('Nee, nooit')),
    ('yes_sometimes', _('Ja, soms wel')),
    ('yes_mostly', _('Ja, meestal wel')),
    ('yes_always', _('Ja, altijd')),
)

IBD_STOOL_CONTINENCE_CHOICES = (
    ('no_never', _('Nee, nooit')),
    ('yes_sometimes', _('Ja, soms wel')),
    ('yes_regulary', _('Ja, regelmatig')),
)


IBD_STOMA_VERSION_CHOICES = (
    ('colostoma', _('Een stoma voor de dikke darm: Colostoma')),
    ('ileostoma', _('Een stoma van de dunne darm: Ileostoma')),
    ('dont_know', _('Weet ik niet')),
)

IBD_ANAL_PAIN_CHOICES = (
    ('no', _('Nee')),
    ('yes_mild', _('Ja, mild')),
    ('yes_severe', _('Ja, ernstig')),
)

IBD_APPETITE_CHOICES = (
    ('good', _('Goed')),
    ('moderate', _('Matig')),
    ('bad', _('Slecht')),
)

IBD_STOMACH_ACHE_CHOICES = (
    ('no', _('Nee')),
    ('yes_sometimes_mild', _('Ja, soms mild')),
    ('yes_sometimes_severe', _('Ja, soms heftig')),
    ('yes_always_mild', _('Ja, continu mild')),
    ('yes_always_severe', _('Ja, continu heftig')),
)


class IBDNauseaVomitTime(models.Model):
    """
    List of IBD nausea vomit times
    """
    name = models.CharField(max_length=64)

    def __unicode__(self):
        return self.name


class IBDQuestionnaire(QuestionnaireBase):
    """
    IBD questionnaire
    """
    has_stoma = models.CharField(
        choices=IBD_YES_NO_CHOICES,
        max_length=32,
        verbose_name=_('Heeft u nu een stoma?'),
        help_text=_(
            'Om de juiste vragen te kunnen stellen over uw stoelgang' +
            ' en ontlasting, willen we graag weten of u een stoma of' +
            ' een pouch heeft.'))
    has_pouch = models.CharField(
        choices=IBD_YES_NO_CHOICES,
        max_length=32,
        verbose_name=_(
            'Heeft u een pouch? (Een pouch is een chirurgisch' +
            ' aangelegd reservoir voor de ontlasting)'))
    has_pouch_problems = models.CharField(
        null=True,
        blank=True,
        choices=IBD_YES_NO_CHOICES,
        max_length=32,
        verbose_name=_('Heeft u klachten van uw pouch?'))
    pouch_problems = models.TextField(
        null=True,
        blank=True,
        verbose_name=_(
            'Kunt u vertellen welke klachten u heeft van uw pouch?'))

    # Subpage 2A (has_stoma = No)
    # Required is set on form.
    stool_freq = models.CharField(
        null=True,
        blank=True,
        choices=IBD_STOOL_FREQ_CHOICES,
        max_length=32,
        verbose_name=_('Hoeveel keer heeft u gemiddeld per dag ontlasting?'))
    stool_thickness = models.CharField(
        null=True,
        blank=True,
        choices=IBD_STOOL_THICKNESS_CHOICES,
        max_length=32,
        verbose_name=_('Hoe dik is de ontlasting?'))
    stool_liquid_freq = models.CharField(
        null=True,
        blank=True,
        choices=IBD_STOOL_LIQUID_CHOICES,
        max_length=32,
        verbose_name=_('Hoe veel keer per dag is de ontlasting waterdun?'))

    diarrhea_at_night = models.CharField(
        null=True,
        blank=True,
        choices=IBD_YES_NO_CHOICES,
        max_length=32,
        verbose_name=_("Heeft u 's nachts diarree?"))
    stool_has_blood = models.CharField(
        null=True,
        blank=True,
        choices=IBD_STOOL_BLOOD_CHOICES,
        max_length=32,
        verbose_name=_('Zit er bloed bij de ontlasting?'))
    stool_has_slime = models.CharField(
        null=True,
        blank=True,
        choices=IBD_STOOL_SLIME_CHOICES,
        max_length=32,
        verbose_name=_('Zit er slijm bij de ontlasting?'))

    # Subpage 3A (has_stoma = No)
    # Required is set on form.
    stool_urgency = models.CharField(
        null=True,
        blank=True,
        choices=IBD_STOOL_URGENCY_CHOICES,
        max_length=32,
        verbose_name=_('Heeft u last van pijnlijke aandrang?'))
    stool_planning = models.CharField(
        null=True,
        blank=True,
        choices=IBD_STOOL_PLANNING_CHOICES,
        max_length=32,
        verbose_name=_('Kunt u de stoelgang uitstellen als dat moet?'))
    stool_continence = models.CharField(
        null=True,
        blank=True,
        choices=IBD_STOOL_CONTINENCE_CHOICES,
        max_length=32,
        verbose_name=_('Verliest u wel eens ongewild wat ontlasting?'))

    # Subpage 2B (has_stoma = yes)
    # Required is set on form.
    stoma_version = models.CharField(
        null=True,
        blank=True,
        choices=IBD_STOMA_VERSION_CHOICES,
        max_length=32,
        verbose_name=_('Wat voor stoma heeft u?'))
    stoma_empty_freq = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Hoe vaak moet u uw stomazakje legen?' +
                       ' (aantal x per 24 uur)'))
    stoma_has_problems = models.CharField(
        null=True,
        blank=True,
        choices=IBD_YES_NO_CHOICES,
        max_length=32,
        verbose_name=_('Zijn er momenteel problemen met uw stoma?'))
    stoma_problems = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Welke problemen heeft u met het stoma?'))

    # Subpage 4
    nausea_vomit = models.CharField(
        choices=IBD_YES_NO_CHOICES,
        max_length=32,
        verbose_name=_('Heeft u last van misselijkheid of braken?'))
    nausea_vomit_time = ManyToManyField(
        IBDNauseaVomitTime,
        blank=True,
        verbose_name=_('Wanneer heeft u last van misselijkheid of braken?'))
    has_fistel = models.CharField(
        choices=IBD_YES_NO_UNKNOWN_CHOICES,
        max_length=32,
        verbose_name=_('Heeft u nu fistels?'))
    fistel_location = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Kunt u aangeven waar de fistels zich bevinden?'))
    anal_pain = models.CharField(
        choices=IBD_ANAL_PAIN_CHOICES,
        max_length=32,
        verbose_name=_('Heeft u last van anale pijn?'))
    anal_problems = models.CharField(
        choices=IBD_YES_NO_CHOICES,
        max_length=32,
        verbose_name=_('Heeft u een of meer anale fissuren, anale fistels' +
                       ' of anale abcessen?'))

    # Subpage 5
    appetite = models.CharField(
        choices=IBD_APPETITE_CHOICES,
        max_length=32,
        verbose_name=_('Hoe is uw eetlust?'))
    patient_weight = models.DecimalField(
        verbose_name=_('Hoeveel weegt u op dit moment? (in kg)'),
        decimal_places=3,
        max_digits=6,
        help_text=_('kg'))
    patient_length = models.DecimalField(
        verbose_name=_('Hoe lang bent u? (in cm)'),
        decimal_places=2,
        max_digits=5,
        help_text=_('cm'))
    stomach_ache = models.CharField(
        choices=IBD_STOMACH_ACHE_CHOICES,
        max_length=32,
        verbose_name=_('Heeft u last van buikpijn?'))
    fatigue = models.CharField(
        choices=IBD_YES_NO_CHOICES,
        max_length=32,
        verbose_name=_('Heeft u last van moeheid?'))
    fever = models.CharField(
        choices=IBD_YES_NO_CHOICES,
        max_length=32,
        verbose_name=_('Heeft u sinds de laatste controle koorts gehad?'))
    fever_specify = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Kunt u vertellen wanneer u koorts had en' +
                       ' hoe hoog uw koorts was?'))

    # Subpage 6
    joint_pain = models.CharField(
        choices=IBD_YES_NO_CHOICES,
        max_length=32,
        verbose_name=_('Heeft u last van gewrichtspijn?'))
    joint_pain_complaints = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Welke klachten heeft u hiervan?'))
    eye_inflammation = models.CharField(
        choices=IBD_YES_NO_CHOICES,
        max_length=32,
        verbose_name=_('Heeft u last van oogonstekingen?'))
    eye_inflammation_complaints = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Welke klachten heeft u hiervan?'))
    skin_disorder = models.CharField(
        choices=IBD_YES_NO_CHOICES,
        max_length=32,
        verbose_name=_('Heeft u last van huidafwijkingen?'))
    skin_disorder_complaints = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Welke klachten heeft u hiervan?'))

    # Subpage ..
    # Medication is not included yet
    # has_medication = models.CharField(choices=IBD_YES_NO_CHOICES,
    # max_length=32, verbose_name=_('Gebruikt u medicatie?'))
    # has_medication_specify = models.TextField(null=True,
    # blank=True, verbose_name=_('Kunt u hieronder aangeven welke medicatie?'))

    # Subpage 7
    does_smoke = models.CharField(
        choices=IBD_YES_NO_CHOICES,
        max_length=32,
        verbose_name=_('Rookt u?'))
    smoke_freq = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Hoeveel sigaretten (of sigaren) rookt u per dag?'))
    question_remarks = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Heeft u verder nog vragen of opmerkingen' +
                       ' voor uw arts?'))

    @property
    def display_template(self):
        """
        Returns:
            The template path & name to be used for showing the details
            page for the filled in data for this questionnaire.
        """
        return 'questionnaire/details/IBDQuestionnaire.html'

    @property
    def BMI(self):
        '''
        Function for calculating the BMI
        '''
        # not divide by 0
        if self.patient_length == 0:
            return None

        # Fix for template
        if isinstance(self.patient_length, unicode):
            self.patient_length = Decimal(self.patient_length)
        if isinstance(self.patient_weight, unicode):
            self.patient_weight = Decimal(self.patient_weight)

        length = self.patient_length / 100
        # print (self.patient_length*self.patient_length)
        return round(self.patient_weight / (length * length), 1)

    @property
    def graphic_score_display(self):
        return str(self.BMI).replace(',', '.')

    @property
    def graphic_score_max(self):
        return 40

    @property
    def graphic_score_min(self):
        return 10

    @property
    def graphic_score_name(self):
        return _('BMI')

    # display name
    display_name = _('Ziekteactiviteit')

    lower_case_name = 'ibd_questionnaire'
