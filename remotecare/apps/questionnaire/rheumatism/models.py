# -*- coding: utf-8 -*-
"""
This module contains all the rheumatism
questionnaire models

:subtitle:`Class definitions:`
"""
from django.db import models
from django.utils.translation import ugettext as _
from apps.questionnaire.models import QuestionnaireBase

RADAI_DEFAULT_SCORE = (
    ('none', _('Niet')),
    ('almost_unnoticeable', _('Bijna onmerkbaar')),
    ('minimal_to_mild', _('Minimaal tot mild')),
    ('mild', _('Mild')),
    ('mild_to_moderate', _('Mild tot matig')),
    ('moderate', _('Matig')),
    ('moderate_to_severe', _('Matig tot hevig')),
    ('severe', _('Hevig')),
    ('severe_to_extreme', _('Hevig tot extreem')),
    ('extreme', _('Extreem')),

)

RADAI_STIFFNESS_SCORE = (
    ('none', _('Geen')),
    ('less_30min', _('< 30 min')),
    ('30_to_60min', _('30-60 min')),
    ('1_to_2hours', _('1-2 uur')),
    ('2_to_4hours', _('2-4 uur')),
    ('4_to_less1day', _('> 4 uur maar niet de hele dag')),
    ('all_day', _('Hele dag')),
)

RADAI_PAIN_SCORE = (
    ('none', _('Geen')),
    ('mild', _('Mild')),
    ('moderate', _('Matig')),
    ('severe', _('Hevig')),
)


# Rheumatoid arthritis Disease Activity Ondex (RADAI) Questionnaire
class RADAIQuestionnaire(QuestionnaireBase):
    """
    Rheumatoid arthritis Disease Activity Ondex (RADAI) Questionnaire
    """
    activity_six_month_score = models.CharField(
        choices=RADAI_DEFAULT_SCORE,
        max_length=32,
        verbose_name=_(
            'Hoe actief is de artritis geweest de afgelopen 6 maanden?'))
    activity_today_score = models.CharField(
        choices=RADAI_DEFAULT_SCORE,
        max_length=32,
        verbose_name=_(
            'Hoe actief is de artritis vandaag in termen van' +
            ' gewrichtsgevoeligheid en zwelling?'))
    pain_today_score = models.CharField(
        choices=RADAI_DEFAULT_SCORE,
        max_length=32,
        verbose_name=_('Hoeveel artritis pijn ervaart u vandaag?'))
    stiffness_today_score = models.CharField(
        choices=RADAI_STIFFNESS_SCORE,
        max_length=32,
        verbose_name=_(
            'Hoe lang voelde u stijfheid van de gewrichten vandaag?'))

    # left pain scores
    left_shoulder_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Linker schouder'))
    left_elbow_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Linker elleboog'))
    left_wrist_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Linker pols'))
    left_vingers_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Linker vingers'))
    left_hip_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Linker heup'))
    left_knee_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Linker knie'))
    left_ankle_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Linker enkel'))
    left_toes_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Linker tenen'))

    # right pain scores
    right_shoulder_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Rechter schouder'))
    right_elbow_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Rechter elleboog'))
    right_wrist_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Rechter pols'))
    right_vingers_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Rechter vingers'))
    right_hip_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Rechter heup'))
    right_knee_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Rechter knie'))
    right_ankle_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Rechter enkel'))
    right_toes_pain_score = models.CharField(
        choices=RADAI_PAIN_SCORE,
        max_length=32,
        verbose_name=_('Rechter tenen'))
    # display name
    display_name = _('Ziekteactiviteit')
    lower_case_name = 'radaiquestionnaire'

    @property
    def graphic_score_display(self):
        """
        Returns:
            The graphic score display to use for the graphic
        """
        # count of left/right pain scores
        count = 0
        for field in self._meta.fields:
            if 'right_' in field.name or 'left_' in field.name:
                if getattr(self, field.name) not in ('none', '', None):
                    count = count + 1
        return count

    def graphic_score_max(self):
        return 16

    def graphic_score_min(self):
        return 0

    def graphic_score_name(self):
        return _('Pijnlijke gewrichten')

    @property
    def display_template(self):
        """
        Returns:
            The template path & name to be used for showing the details
            page for the filled in data for this questionnaire.
        """
        return 'questionnaire/details/RADAIQuestionnaire.html'

HEALTH_GENERAL_SCORE = (
    ('excellent', _('Uitstekend')),
    ('very_good', _('Zeer goed')),
    ('good', _('Goed')),
    ('poor', _('Matig')),
    ('bad', _('Slecht')),
)

HEALTH_CHANGES_SCORE = (
    ('much_better', _('Veel beter dan een jaar geleden')),
    ('slighty_better', _('Iets beter dan een jaar geleden')),
    ('about_same', _('Ongeveer hetzelfde als een jaar geleden')),
    ('slighty_worse', _('Iets slechter dan een jaar geleden')),
    ('much_worse', _('Veel slechter dan een jaar geleden')),
)

EFFORT_SCORE = (
    ('severe', _('Ja, ernstig beperkt')),
    ('a_bit', _('Ja, een beetje beperkt')),
    ('not', _('Nee, helemaal niet beperkt')),
)

PROBLEM_SCORE = (
    ('yes', _('Ja')),
    ('no', _('Nee')),
)

SOCIAL_IMPACT_SCORE = (
    ('nothing', _('Helemaal niet')),
    ('a_bit', _('Enigzins')),
    ('a_lot', _('Nogal')),
    ('much', _('Veel')),
    ('verry_much', _('Heel erg veel')),
)

PAIN_SCORE = (
    ('none', _('Geen')),
    ('really_light', _('Heel licht')),
    ('light', _('Licht')),
    ('a_lot', _('Nogal')),
    ('severe', _('Ernstig')),
    ('really_severe', _('Heel ernstig')),
)

PAIN_IMPACT_SCORE = (
    ('none', _('Helemaal niet')),
    ('a_bit', _('Een klein beetje')),
    ('a_lot', _('Nogal')),
    ('much', _('Veel')),
    ('verry_much', _('Heel erg veel')),
)

FEELING_SCORE = (
    ('non_stop', _('Voortdurend')),
    ('often', _('Meestal')),
    ('frequently', _('Vaak')),
    ('sometimes', _('Soms')),
    ('rarely', _('Zelden')),
    ('never', _('Nooit')),
)

SOCIAL_IMPACT2_SCORE = (
    ('non_stop', _('Voortdurend')),
    ('often', _('Meestal')),
    ('sometimes', _('Soms')),
    ('rarely', _('Zelden')),
    ('never', _('Nooit')),
)

RELATIVATION_SCORE = (
    ('correct', _('Volkomen juist')),
    ('partly_correct', _('Grotendeels juist')),
    ('dontknow', _('Weet ik niet')),
    ('party_incorrect', _('Grotendeels onjuist')),
    ('incorrect', _('Volkomen onjuist')),
)


class RheumatismSF36(QuestionnaireBase):
    """
    Rheumatoid arthritis SF36 questionnaire
    """
    health_general = models.CharField(
        choices=HEALTH_GENERAL_SCORE,
        max_length=32,
        verbose_name=_(
            'Wat vindt u, over het algemeen genomen, van uw gezondheid?'))
    health_changes = models.CharField(
        choices=HEALTH_CHANGES_SCORE,
        max_length=32,
        verbose_name=_(
            'In vergelijking met een jaar geleden, hoe zou u nu uw'
            'gezondheid in het algemeen beoordelen?'))

    # Daily effortsStartUrgentQuestionnare
    high_effort_impact = models.CharField(
        choices=EFFORT_SCORE,
        max_length=32,
        verbose_name=_(
            'Forse inspanning zoals hardlopen, zware voorwerpen tillen,' +
            ' inspannend sporten'),
        help_text=_(
            'De volgende vragen gaan over uw dagelijkse bezigheden. Wordt' +
            ' u door uw gezondheid op dit moment beperkt bij' +
            'deze bezigheden? Zo ja, in welke mate?'))
    poor_effort_impact = models.CharField(
        choices=EFFORT_SCORE,
        max_length=32,
        verbose_name=_(
            'Matige inspanning zoals het verplaatsen van een tafel,' +
            ' stofzuigen, fietsen'))
    carrying_impact = models.CharField(
        choices=EFFORT_SCORE,
        max_length=32,
        verbose_name=_('Tillen of boodschappen dragen'))
    walking_stairs_impact = models.CharField(
        choices=EFFORT_SCORE,
        max_length=32,
        verbose_name=_('Een paar trappen oplopen'))
    walking_one_stair_impact = models.CharField(
        choices=EFFORT_SCORE,
        max_length=32,
        verbose_name=_(u'Eén trap oplopen'))
    bent_over_impact = models.CharField(
        choices=EFFORT_SCORE,
        max_length=32,
        verbose_name=_('Buigen, knielen of bukken'))
    walk_km_impact = models.CharField(
        choices=EFFORT_SCORE,
        max_length=32,
        verbose_name=_('Meer dan een kilometer lopen'))
    walk_halfkm_impact = models.CharField(
        choices=EFFORT_SCORE,
        max_length=32,
        verbose_name=_('Een halve kilometer lopen'))
    walk_tenthkm_impact = models.CharField(
        choices=EFFORT_SCORE,
        max_length=32,
        verbose_name=_('Honderd meter lopen'))
    wash_cloth_impact = models.CharField(
        choices=EFFORT_SCORE,
        max_length=32,
        verbose_name=_('Uzelf wassen of aankleden'))

    # Fysical problems
    work_less_problem = models.CharField(
        choices=PROBLEM_SCORE,
        max_length=32,
        verbose_name=_(
            'U heeft minder tijd kunnen besteden aan werk of' +
            ' andere bezigheden'),
        help_text=_(
            u'Had u, ten gevolge van uw lichamelijke gezondheid,' +
            u' de afgelopen 4 weken één van de volgende problemen bij' +
            u' uw werk of andere dagelijkse bezigheden?'))
    achieve_problem = models.CharField(
        choices=PROBLEM_SCORE,
        max_length=32,
        verbose_name=_('U heeft minder bereikt dan u zou willen'))
    work_limitation_problem = models.CharField(
        choices=PROBLEM_SCORE,
        max_length=32,
        verbose_name=_(
            'U was beperkt in het soort werk of het soort bezigheden'))
    work_effort_problem = models.CharField(
        choices=PROBLEM_SCORE,
        max_length=32,
        verbose_name=_(
            'U had moeite met het werk of andere bezigheden' +
            ' (het kostte u bijvoorbeeld extra inspanning)'))

    # Emotional problems
    work_less_emotional_problem = models.CharField(
        choices=PROBLEM_SCORE,
        max_length=32,
        verbose_name=_(
            'U heeft minder tijd kunnen besteden aan werk' +
            ' of andere bezigheden'),
        help_text=_(
            u'Had u, ten gevolge van een emotioneel probleem' +
            u' (bijvoorbeeld doordat u zich depressief of angstig voelde)' +
            u' de afgelopen 4 weken één van de volgende problemen'
            u' bij uw werk of andere dagelijkse bezigheden?'))
    achieve_emotional_problem = models.CharField(
        choices=PROBLEM_SCORE,
        max_length=32,
        verbose_name=_('U heeft minder bereikt dan u zou willen'))
    accurate_emotional_problem = models.CharField(
        choices=PROBLEM_SCORE,
        max_length=32,
        verbose_name=_(
            'U heeft het werk of andere bezigheden niet zo' +
            ' zorgvuldig gedaan als u gewend bent'))

    # Social impact
    social_impact = models.CharField(
        choices=SOCIAL_IMPACT_SCORE,
        max_length=32,
        verbose_name=_(
            'In hoeverre heeft uw lichamelijke gezondheid of hebben' +
            ' uw emotionele problemen u de afgelopen 4 weken belemmerd' +
            ' in uw normale sociale bezigheden met gezin, vrienden,' +
            ' buren of anderen?'))

    # Pain
    pain_score = models.CharField(
        choices=PAIN_SCORE,
        max_length=32,
        verbose_name=_('Hoeveel pijn had u de afgelopen 4 weken?'))

    # Pain impact
    pain_impact = models.CharField(
        choices=PAIN_IMPACT_SCORE,
        max_length=32,
        verbose_name=_(
            'In welke mate heeft pijn u de afgelopen 4 weken belemmerd' +
            ' bij uw normale werkzaamheden (zowel werk, buitenhuis als' +
            ' huishoudelijk werk)?'))

    # Feeling
    cheerful_score = models.CharField(
        choices=FEELING_SCORE,
        max_length=32,
        verbose_name=_('Voelde u zich levenslustig?'),
        help_text=_('Hoe vaak gedurende de afgelopen 4 weken:'))
    nervious_score = models.CharField(
        choices=FEELING_SCORE,
        max_length=32,
        verbose_name=_('Voelde u zich erg zenuwachtig?'))
    blues_score = models.CharField(
        choices=FEELING_SCORE,
        max_length=32,
        verbose_name=_('Zat u zo in de put dat niets u kon opvrolijken?'))
    calm_score = models.CharField(
        choices=FEELING_SCORE,
        max_length=32,
        verbose_name=_('Voelde u zich kalm en rustig?'))
    energetic_score = models.CharField(
        choices=FEELING_SCORE,
        max_length=32,
        verbose_name=_('Voelde u zich energiek?'))
    depressed_score = models.CharField(
        choices=FEELING_SCORE,
        max_length=32,
        verbose_name=_('Voelde u zich neerslachtig en somber?'))
    burnout_score = models.CharField(
        choices=FEELING_SCORE,
        max_length=32,
        verbose_name=_('Voelde u zich uitgeblust?'))
    happiness_score = models.CharField(
        choices=FEELING_SCORE,
        max_length=32,
        verbose_name=_('Voelde u zich gelukkig?'))
    tired_score = models.CharField(
        choices=FEELING_SCORE,
        max_length=32,
        verbose_name=_('Voelde u zich moe?'))

    # Social visiting other people impact
    social_visit_impact = models.CharField(
        choices=SOCIAL_IMPACT2_SCORE,
        max_length=32,
        verbose_name=_(
            'Hoe vaak hebben uw lichamelijke gezondheid of uw emotionele' +
            ' problemen gedurende de afgelopen 4 weken uw sociale' +
            ' activiteiten (zoals bezoek aan vrienden of naaste' +
            ' familieleden) belemmerd?'))

    # Relativation
    easier_ill_score = models.CharField(
        choices=RELATIVATION_SCORE,
        max_length=32,
        verbose_name=_(
            'Ik lijk gemakkelijker ziek te worden dan andere mensen'),
        help_text=_(
            'Wilt u het antwoord kiezen dat het beste weergeeft hoe' +
            ' juist of onjuist u elk van de volgende uitspraken voor' +
            ' uzelf vindt?'))
    even_healthy_score = models.CharField(
        choices=RELATIVATION_SCORE,
        max_length=32,
        verbose_name=_('Ik ben net zo gezond als andere mensen die ik ken'))
    health_drop_score = models.CharField(
        choices=RELATIVATION_SCORE,
        max_length=32,
        verbose_name=_('Ik verwacht dat mijn gezondheid achteruit zal gaan'))
    excellent_health_score = models.CharField(
        choices=RELATIVATION_SCORE,
        max_length=32,
        verbose_name=_('Mijn gezondheid is uitstekend'))

    @property
    def display_template(self):
        """
        Returns:
            The template path & name to be used for showing the details
            page for the filled in data for this questionnaire.
        """
        return 'questionnaire/details/RheumatismSF36.html'

    @property
    def graphic_score_display(self):
        """
        Returns:
            the score for in the graphic
        """
        # count of left/right pain scores
        count = 0
        for index, item in enumerate(HEALTH_GENERAL_SCORE):
            if item[0] == self.health_general:
                count = self.graphic_score_max - index
        return count

    @property
    def graphic_score_max(self):
        return 5

    @property
    def graphic_score_min(self):
        return 0

    @property
    def graphic_score_name(self):
        return _('Algemene gezondheid')

    # display name
    display_name = _('Kwaliteit van leven')

    lower_case_name = 'rheumatismsf36'
