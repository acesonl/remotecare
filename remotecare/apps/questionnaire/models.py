# -*- coding: utf-8 -*-
"""
This module contains the questionnaire model definitions which both includes
the generic questionnaire parts as well as the disease specific questionnaire
model definitions.

The main entry point for a control is the :class:`QuestionnaireRequest` which
can have multiple related :class:`RequestStep` instances. Every questionnaire
is a subclass of :class:`QuestionnaireBase` which is coupled to a RequestStep.
The :class:`WizardDatabaseStorage` model is used to temporarily store
the data. The relationships are shown in the following model diagram:

.. graphviz:: ../../_static/questionnaire.dot

Questionnaires models and associated forms should be included into their own
apps. For each added questionnaire model the PACKAGE_LOCATION dict needs to
be updated. This dict is used by both the get_model_class method in this
module as well as the get_forms_for method in the forms.py module.

Models can be defined as the following the example:

.. code-block:: python

    class IBDQuestionnaire(QuestionnaireBase):
        #Make sure to subclass QuestionnaireBase

        #Add this property to return a template that can be used
        #to display all the filled in values, see other templates
        #for the basic layout.
        @property
        def display_template(self):
            return 'questionnaire/details/IBDQuestionnaire.html'

        #Returns the graphic score to display in the graphic
        # Currently only works for a couple predefined questionnaire
        # categories: Ziekteactiviteit, kwaliteitvanleven, kwaliteitvanzorg
        @property
        def graphic_score_display(self):
            return str(self.BMI).replace(',', '.')

        #The axis maximum score for the graph
        @property
        def graphic_score_max(self):
            return 40

        #The axis minimum score for the graph
        @property
        def graphic_score_min(self):
            return 10

        #The axis score name to set for the graphic
        @property
        def graphic_score_name(self):
            return _('BMI')

        #The category of this questionnaire and also the name to display
        display_name = _('Ziekteactiviteit')

        #The lower case name of this questionnaire
        lower_case_name = 'ibd_questionnaire'


.. note:: After adding new questionnaires make
          sure to update the PACKAGE_LOCATION dict in models.py

:subtitle:`Class and function definitions:`
"""
import importlib
from datetime import timedelta
from django.db import models
from django.utils.translation import ugettext as _
from core.models import DateField, AuditBaseModel

from apps.healthperson.patient.models import Patient, DIAGNOSIS_CHOICES
from apps.healthperson.healthprofessional.models import HealthProfessional
from apps.healthperson.secretariat.models import Secretary

from calendar import timegm


# Definitions where to find the models and forms.
#
# Add new questionnaire models to this list like:
# (model_name, full_package_path)
PACKAGE_LOCATION = {
    'IBDQuestionnaire': 'apps.questionnaire.ibd',
    'RheumatismSF36': 'apps.questionnaire.rheumatism',
    'RADAIQuestionnaire': 'apps.questionnaire.rheumatism',
    'QOHCQuestionnaire': 'apps.questionnaire.qohc',
    'QOLQuestionnaire': 'apps.questionnaire.qol',
    'QOLChronCUQuestionnaire': 'apps.questionnaire.qol',
    'StartQuestionnaire': 'apps.questionnaire.default',
    'StartUrgentQuestionnaire': 'apps.questionnaire.default',
    'UrgentProblemQuestionnaire': 'apps.questionnaire.default',
    'FinishQuestionnaire': 'apps.questionnaire.default'
    }

# Choices definition for the RequestStep model
#
# Add new questionnaires to the list
AVAILABLE_QUESTIONNAIRES = (
    ('StartQuestionnaire', _('001 Hoe gaat het met u?')),
    ('IBDQuestionnaire',
        _('002 Ziekteactiviteit - Ziekte van Chron en Colitis Ulcerosa')),
    ('RADAIQuestionnaire',
        _('003 Ziekteactiviteit - Rheumatoide artritis - RADAI vragenlijst')),
    ('QOLChronCUQuestionnaire',
        _('004 Kwaliteit van het leven -' +
          ' Ziekte van Chron en Colitis Ulcerosa (deel lastmeter)')),
    ('QOLQuestionnaire',
        _('005 Kwaliteit van het leven -' +
          ' Dunnedarmtransplantatie (lastmeter)')),
    ('RheumatismSF36', _('006 Kwaliteit van het leven -' +
                         ' SF36 Reumatoide artritis')),
    ('QOHCQuestionnaire',
        _('007 Kwaliteit van zorg vragenlijst')),
    ('FinishQuestionnaire', _('008 Afspraak, bloedprikken en afsluiting')),
    ('StartUrgentQuestionnaire', _('009 Direct een afspraak')),
    ('UrgentProblemQuestionnaire', _('010 Omschrijving problemen')),
)

# Default control questionnaire list
# defines the questionnaires per disease
# Add definitions for new diagnoses
AVAILABLE_CONTROL_QUESTIONNAIRE_LIST = (
    ('rheumatoid_arthritis', ('StartQuestionnaire',
                              'RADAIQuestionnaire',
                              'RheumatismSF36',
                              'QOHCQuestionnaire',
                              'FinishQuestionnaire',)),
    ('colitis_ulcerosa', ('StartQuestionnaire',
                          'IBDQuestionnaire',
                          'QOLChronCUQuestionnaire',
                          'QOHCQuestionnaire',
                          'FinishQuestionnaire',)),
    ('chron', ('StartQuestionnaire',
               'IBDQuestionnaire',
               'QOLChronCUQuestionnaire',
               'QOHCQuestionnaire',
               'FinishQuestionnaire',)),
    ('intestinal_transplantation', ('StartQuestionnaire',
                                    'QOLQuestionnaire',
                                    'QOHCQuestionnaire',
                                    'FinishQuestionnaire',)),
)

# List with possibilities of questionnaires
# that can be exclude during a control per diagnose
QUESTIONNAIRE_EXCLUDE_LIST = (
    ('rheumatoid_arthritis', ('RADAIQuestionnaire',
                              'RheumatismSF36',)),
    ('colitis_ulcerosa', ('IBDQuestionnaire',
                          'QOLChronCUQuestionnaire',
                          'QOHCQuestionnaire',)),
    ('chron', ('IBDQuestionnaire',
               'QOLChronCUQuestionnaire',
               'QOHCQuestionnaire',)),
    ('intestinal_transplantation', ('QOLQuestionnaire',
                                    'QOHCQuestionnaire',)),
)


# Urgent questionnaire list
# add entries for extra diagnoses
AVAILABLE_URGENT_QUESTIONNAIRE_LIST = (
    ('rheumatoid_arthritis', ('StartUrgentQuestionnaire',
                              'UrgentProblemQuestionnaire',
                              'RADAIQuestionnaire',
                              'RheumatismSF36',)),
    ('colitis_ulcerosa', ('StartUrgentQuestionnaire',
                          'UrgentProblemQuestionnaire',
                          'IBDQuestionnaire',
                          'QOLChronCUQuestionnaire',)),
    ('chron', ('StartUrgentQuestionnaire',
               'UrgentProblemQuestionnaire',
               'IBDQuestionnaire',
               'QOLChronCUQuestionnaire',)),
    ('intestinal_transplantation', ('StartUrgentQuestionnaire',
                                    'UrgentProblemQuestionnaire',
                                    'QOLQuestionnaire',)),
)


def get_model_class(model_class_name):
    """
    Get the model_class by the model_name, uses the PACKAGE_LOCATION
    list to get the package location.

    Args:
        - model_class_name: the model class name (case sensitive)

    Returns:
        The model class for model_class_name
    """
    module = importlib.import_module(
        PACKAGE_LOCATION[model_class_name] + '.models')
    return getattr(module, model_class_name)


# QuestionnarieRequest
class QuestionnaireRequest(AuditBaseModel):
    """
    The questionnaire request is the base for a periodic control. It
    couples the patient to the request steps which specify the questionnaire
    models that need to be filled in by the patient.

    It also keeps tracks of the questionnaire status like the deadline,
    finished_date and read_on date.
    """
    patient = models.ForeignKey(Patient)

    # Is urgent request (created by patient self)?
    urgent = models.BooleanField(default=False)

    # Practitioner on moment of creating the request or in case of an urgent
    # request while filling in questionnaire
    practitioner = models.ForeignKey(HealthProfessional)

    # Deadline settings
    deadline_nr = models.IntegerField(blank=True, null=True)
    deadline = DateField(blank=True,
                         null=True,
                         future=True,
                         verbose_name=_('Deadline'))
    # Patient statuses
    created_on = models.DateField(auto_now_add=True)
    finished_on = models.DateField(null=True, blank=True)

    # healthprofessional read the questionnaire answers
    read_on = models.DateField(blank=True, null=True)

    # patient_diagnose for this questionnaire
    patient_diagnose = models.CharField(
        choices=DIAGNOSIS_CHOICES,
        max_length=128,
        verbose_name=_('Diagnose'))

    # True if the questionnaires is saved to be finished later
    saved_finish_later = models.BooleanField(default=False)

    # last filled in requeststep and form step
    last_filled_in_step = models.CharField(null=True, blank=True, max_length=4)
    last_filled_in_form_step = models.CharField(
        null=True,
        blank=True,
        max_length=4)

    # report handling statuses, used for healthprofessional views
    handled_on = models.DateField(null=True, blank=True)
    handled_by = models.ForeignKey(
        HealthProfessional,
        related_name='handled_by',
        null=True,
        blank=True)

    # appointment statuses, used for secretary views
    appointment_needed = models.BooleanField(default=False)
    appointment_added_on = models.DateField(null=True, blank=True)
    appointment_added_by = models.ForeignKey(Secretary, null=True, blank=True)

    @property
    def filled_in(self):
        """
        Returns:
            True if the finished_on is set else False
        """
        return self.finished_on is not None

    @property
    def handled(self):
        """
        Returns:
            True if the handled_on is set else False
        """
        return self.handled_on is not None

    @property
    def appointment_arranged(self):
        """
        Returns:
            Ja if the appointment is arranged else Nee
        """
        if self.appointment_added_on:
            return _('Ja')
        return _('Nee')

    @property
    def appointment_on_short_term(self):
        """
        Returns:
            True if the appointment is on short term else False
        """
        from apps.questionnaire.default.models import FinishQuestionnaire,\
            StartUrgentQuestionnaire

        if not self.filled_in:
            return False

        request_steps = self.requeststep_set.all().order_by('step_nr')
        if not self.urgent:
            finishquestionnaire = FinishQuestionnaire.objects.get(
                request_step=request_steps[
                    request_steps.count() -
                    1])
            appointment_period = finishquestionnaire.appointment_period
            if appointment_period != 'within_4_weeks':
                return True
        else:
            # find starturgentquestionnaire = the first questionnaire step
            starturgentquestionnaire = StartUrgentQuestionnaire.objects.get(
                request_step=request_steps[0])
            appointment_period = starturgentquestionnaire.appointment_period
            if appointment_period != 'this_week':
                return True
        return False

    @property
    def blood_taken(self):
        """
        Returns:
            True if blood taken question is answered postive or False
        """
        from apps.questionnaire.default.models import FinishQuestionnaire

        if not self.urgent:
            request_steps = self.requeststep_set.all().order_by('step_nr')
            # find finishquestionnaire = the last questionnaire step
            finishquestionnaire = FinishQuestionnaire.objects.get(
                request_step=request_steps[
                    request_steps.count() -
                    1])
            if finishquestionnaire.blood_sample:
                if finishquestionnaire.blood_sample not in ('', None, 'None'):
                    return _('Ja')
        return _('Nee')

    @property
    def blood_taken_date(self):
        """
        Returns:
            The last blood taken date or None
        """
        from apps.questionnaire.default.models import FinishQuestionnaire

        if not self.urgent:
            request_steps = self.requeststep_set.all().order_by('step_nr')
            # find finishquestionnaire = the last questionnaire step
            finishquestionnaire = FinishQuestionnaire.objects.get(
                request_step=request_steps[
                    request_steps.count() -
                    1])
            return finishquestionnaire.blood_sample_date
        return None

    @property
    def patient_needs_appointment(self):
        """
        Returns:
            True if the patient needs to have an appointment else False
        """
        from apps.questionnaire.default.models import FinishQuestionnaire

        if not self.filled_in:
            return False

        # returns true if the patient has requested an appointment
        if not self.urgent:
            request_steps = self.requeststep_set.all().order_by('step_nr')
            # find finishquestionnaire = the last questionnaire step
            finishquestionnaire = FinishQuestionnaire.objects.get(
                request_step=request_steps[
                    request_steps.count() -
                    1])
            if finishquestionnaire.appointment == 'no':
                return False

        # Urgent is always true
        return True

    @property
    def appointment_period_date(self):
        """
        Returns:
            The appointment period date or None
        """
        from apps.questionnaire.default.models import FinishQuestionnaire,\
            StartUrgentQuestionnaire

        request_steps = self.requeststep_set.all().order_by('step_nr')
        appointment_period_date = self.finished_on

        if not self.filled_in:
            return appointment_period_date

        if self.urgent:
            # find starturgentquestionnaire = the first questionnaire step
            starturgentquestionnaire = StartUrgentQuestionnaire.objects.get(
                request_step=request_steps[0])
            appointment_period = starturgentquestionnaire.appointment_period

            delta_days = 0
            if appointment_period == 'tommorow':
                delta_days = 1
            elif appointment_period == 'within_3_days':
                delta_days = 3
            elif appointment_period == 'this_week':
                delta_days = 7

            appointment_period_date = appointment_period_date + \
                timedelta(days=delta_days)
        else:
            # find finishquestionnaire = the last questionnaire step

            finishquestionnaire = FinishQuestionnaire.objects.get(
                request_step=request_steps[
                    request_steps.count() -
                    1])
            appointment_period = finishquestionnaire.appointment_period

            delta_days = 0
            if appointment_period == 'within_4_weeks':
                delta_days = 28
            elif appointment_period == 'within_2_weeks':
                delta_days = 14
            elif appointment_period == 'this_week':
                delta_days = 7

            appointment_period_date = appointment_period_date + \
                timedelta(days=delta_days)

        return appointment_period_date

    @property
    def appointment_period(self):
        """
        Returns:
            The appointment period or None
        """
        from apps.questionnaire.default.models import FinishQuestionnaire,\
            StartUrgentQuestionnaire

        request_steps = self.requeststep_set.all().order_by('step_nr')
        appointment_period = None

        if not self.filled_in:
            return appointment_period

        if self.urgent:
            # find starturgentquestionnaire = the first questionnaire step
            starturgentquestionnaire = StartUrgentQuestionnaire.objects.get(
                request_step=request_steps[0])
            appointment_period =\
                starturgentquestionnaire.get_appointment_period_display()
        else:
            # find finishquestionnaire = the last questionnaire step

            finishquestionnaire = FinishQuestionnaire.objects.get(
                request_step=request_steps[
                    request_steps.count() -
                    1])

            appointment_period =\
                finishquestionnaire.get_appointment_period_display()

            if finishquestionnaire.appointment_preference:
                if ((finishquestionnaire.appointment_preference not in
                     ('', None, 'None'))):
                    appointment_period = appointment_period + \
                        _(' bij voorkeur op: ') +\
                        finishquestionnaire.appointment_preference

        return appointment_period


# Step in the questionnaire request.
class RequestStep(models.Model):
    """
    The requeststep model is coupled to the :class:`QuestionnaireRequest` and
    is used to store the questionnaire steps of the control.

    Every step is coupled to one and only one Questionnaire model class. Which
    this model class the forms are initalized and displayed to the user with
    help of the wizard.

    The step_nr field is used for sorting.
    """
    questionnairerequest = models.ForeignKey(QuestionnaireRequest)
    step_nr = models.IntegerField()
    model = models.CharField(
        choices=AVAILABLE_QUESTIONNAIRES,
        max_length=256,
        verbose_name=_('Kies vragenlijst'))

    @property
    def model_class(self):
        """
            Returns:
                The model_class of associated with the model (name)
                attribute of this RequestStep
        """
        return get_model_class(self.model)

    @property
    def questionnaire(self):
        """
        Returns:
            The filled in questionnaire for this RequestStep or None
        """
        # lazy
        if hasattr(self, '_questionnaire'):
            return self._questionnaire

        try:
            questionnaire = self.model_class.objects.get(request_step=self)
        except self.model_class.DoesNotExist:
            questionnaire = None
        self._questionnaire = questionnaire
        return questionnaire


# Wizard questionnaire database storage
class WizardDatabaseStorage(models.Model):
    """
    Wizard database storage, saves both clean and unclean data in the
    data field in json format. The wizard uses an instance of this
    model to temporarily store all filled in questionnaire data until
    all questionnaires are filled in correctly.
    """
    questionnaire_request = models.ForeignKey(QuestionnaireRequest)
    data = models.TextField(blank=True, null=True)
    created_on = models.DateField(auto_now_add=True)


# Abstract model for questionnaire
class QuestionnaireBase(AuditBaseModel):
    """
    Abstract class which is the baseclass for every Questionnaire models.
    Couples to one and only one :class:`RequestStep`
    """
    request_step = models.ForeignKey(RequestStep)

    @property
    def patient(self):
        """
        Returns:
            The patient for the questionnaire request associated
            with the requeststep for this the questionnaire
        """
        return self.request_step.questionnairerequest.patient

    @property
    def finished_on(self):
        """
        Returns:
            The finished date of the questionnaire request or None
        """
        request = self.request_step.questionnairerequest
        if not request.finished_on:
            return None
        return request.finished_on

    @property
    def get_finished_on_timestamp(self):
        """
        Returns:
            The finished timestamp of the questionnaire request or None
        """
        request = self.request_step.questionnairerequest
        if not request.finished_on:
            return None
        return timegm(request.finished_on.timetuple()) * 1000

    @property
    def encryption_key(self):
        # This makes getting the key faster
        from apps.account.models import EncryptionKey

        encrypted_key = EncryptionKey.get_with_healthperson_id(
            self.patient_id)
        return EncryptionKey(key=encrypted_key).key

    class Meta:
        abstract = True
