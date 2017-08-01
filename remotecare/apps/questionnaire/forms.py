"""
This module contains the baseclass for all questionnaire forms
and the functions for getting all forms based on a questionnaire model
class.

To add a new form, a new apps needs to be added including a models.py with the
new questionnaire model and a forms.py file with all the new forms.

.. note:: Make sure to update the PACKAGE_LOCATION dict in models.py

Forms can be defined as the following the example:

.. code-block:: python

    class IDBQuestionnaireForm3A(BaseQuestionnaireForm):
        #Forms need to subclass BaseQuestionnaireForm.

        #The form_template which is used rendering the template
        form_template = 'questionnaire/DefaultQuestionnaireForm.html'

        #The number of the form. This number is used to sort the
        #forms when they are retrieved for a model
        form_nr = 3

        #Condition method for conditionally showing the form (True=show)
        #Forms that are not shown are also not validated.
        #The provided wizard argument can be used to get the cleaned
        #data of a form like shown in the example below.
        def condition(self, wizard):
            cleaned_data = wizard.get_cleaned_data_for_form_class(
                IDBQuestionnaireForm)
            if cleaned_data:
                if 'has_stoma' in cleaned_data:
                    if cleaned_data['has_stoma'] == 'yes':
                        return False
            return True

        class Meta:
            model = IBDQuestionnaire

            fieldsets = (
                (None, {'fields': (
                    'stool_urgency', 'stool_planning', 'stool_continence',)}),
            )

            #By using the create_exclude_list method you only have to specify
            #the fieldsets. The excluded list is computed automatically based
            #on the fieldsets en model definition. For multiple forms for one
            #model this saves a lot of time & possibilities for errors.
            exclude = create_exclude_list(model, fieldsets)

The get_forms_for method automatically will pick up the new forms when
the package is added to the PACKAGE_LOCATION dict in models.py.

:subtitle:`Class definitions:`
"""
import inspect
import importlib
from core.forms import BaseModelForm
from apps.questionnaire.models import PACKAGE_LOCATION
# Definitions where to find the forms for every model
# so forms can be saved splitted up


def form_sorting_function(form):
    """
    Simple sorting helper function

    Args:
        - form: a form instance

    Returns:
        The form_nr of the form.
    """
    return form.form_nr


def get_forms_for(questionnaire_model_class):
    """
    Helper function for getting all forms for a questionnaire model class.

    Args:
        - questionnaire_model_class: the class of the questionnaire model.

    Returns:
        A list of forms for a questionnaire model class, sorted on form_nr.
    """
    forms = []

    # import the form.py module from a package by getting
    # package name from the PACKAGE_LOCATION dict from models.py
    module_name =\
        PACKAGE_LOCATION[questionnaire_model_class.__name__] + '.forms'
    module = importlib.import_module(module_name)

    # loop through all members and get the forms for the
    # questionnaire_model_class
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            if issubclass(obj, BaseQuestionnaireForm):
                if obj.Meta.model == questionnaire_model_class:
                    forms.append(obj)

    # sort the forms based on form_nr
    forms.sort(key=form_sorting_function)

    return forms


def create_exclude_list(model, fieldsets):
    """
    Helper method for automatic generating the exclude list
    of fields based on a model and a fieldset definition.
    Allows to only set the fieldsets attribute and use this function
    for the exclude list.

    Args:
        - model: the model to inspect for modelfields
        - fieldsets: the fieldsets that should be included

    Returns:
        A tuple with all model fields excluding the fields in fieldsets
    """
    # Create set of fields to auto populate the exclude list
    fieldset_all_fields = ['id']
    for l in fieldsets:
        for fieldset_field in l[1]['fields']:
            fieldset_all_fields.append(fieldset_field)

    exclude_list = []

    # auto create the exclude list based on fieldsets above
    for field in model._meta.fields:
        if field.name not in fieldset_all_fields:
            exclude_list.append(field.name)

    return tuple(exclude_list)


class BaseQuestionnaireForm(BaseModelForm):
    '''
    Base form for all questionnaires uses
    a form_nr attribute for sorting and a condition
    method for conditionally showing/using the form.
    '''
    # The form_nr attribute is the order in which the forms are shown
    form_nr = 0

    def __init__(self, *args, **kwargs):
        # Add patient to form
        self.patient = kwargs.pop('patient', None)
        super(BaseQuestionnaireForm, self).__init__(*args, **kwargs)

    # Use this function to set a condition
    # for showing the form (True=show form, False=don't show)
    def condition(self, wizard):
        """
        Override this function to allow conditional showing/using forms.
        If the form is not shown it is not validated.

        Args:
            - wizard: the wizard instance that is used to show the forms\
              which can be used to get clean and unclean data of other
              steps/forms to determine if the form should be shown.

        Returns:
            True if the form should be used else False (default=True)
        """
        return True

    class Meta:
        # The model will be set in a subclass
        model = None
