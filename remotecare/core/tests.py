# -*- coding: utf-8 -*-
"""
Remote care specific test that tests things
that were not covered by other tests in the apps.

.. note::
    Needs to be extended with tests for all core code.

:subtitle:`Class definitions:`
"""
import datetime
from django.forms import TextInput
from django.test import TestCase
from core.forms import DisplayWidget, ChoiceOtherField, YesNoChoiceField,\
    FormDateField, NONE_YES_NO_CHOICES
from core.models import YesNoChoiceField as ModelYesNoChoiceField,\
    CheckBoxIntegerField, CheckBoxCharField
from core.widgets import SelectDateWidget


class CoreTests(TestCase):
    """
    Class with tests for modules in the core package
    """

    def check_forms(self):
        """
        Checks parts from the forms module
        """
        # display widget
        display_widget = DisplayWidget()
        display_widget.clean('test')
        display_widget.render('name', 'value')

        choice_other_field = ChoiceOtherField(
            choices=(('1', 1), ('2', 2), ('other', 'other')),
            other_field=TextInput)
        post_data = {'testfield_0': '1'}
        field_name = 'testfield'

        # Check selected value
        choice_other_field.compress(list(post_data))
        choice_other_field.fix_value_from_post(post_data, field_name)
        self.assertIn('testfield', post_data)
        self.assertEqual(post_data['testfield'], '1')

        # Check 'other' value
        post_data = {'testfield_0': 'other', 'testfield_1': 'test'}
        choice_other_field.compress(list(post_data))
        choice_other_field.fix_value_from_post(post_data, field_name)
        self.assertIn('testfield', post_data)
        self.assertEqual(post_data['testfield'], 'test')

        date_field = FormDateField()
        post_data = {'testfield_day': '1',
                     'testfield_month': '1',
                     'testfield_year': '1970'}

        date_field.fix_value_from_post(post_data, field_name)
        self.assertIn('testfield', post_data)
        self.assertEqual(post_data['testfield'], datetime.date(1970, 1, 1))

        yes_no_choicefield = YesNoChoiceField()
        self.assertEqual(
            yes_no_choicefield.widget.choices, NONE_YES_NO_CHOICES)

    def check_models(self):
        """
        Checks parts from the models module
        """
        yes_no_choicefield = ModelYesNoChoiceField()
        self.assertEqual(yes_no_choicefield.formfield().__class__,
                         YesNoChoiceField)

        # Just check that these don't give errors
        check_box_int_field = CheckBoxIntegerField()
        check_box_int_field.formfield()

        check_box_text_field = CheckBoxCharField()
        check_box_text_field.formfield()

    def check_widgets(self):
        """
        Checks parts from the widgets module
        """
        date_widget = SelectDateWidget(years=range(1970, 1980))

        formats = ['n', 'm', 'F', 'b', 'M', 'N', None]
        for fmt in formats:
            date_widget.month_choices(fmt)

        formats = ['j', 'd', None]
        for fmt in formats:
            date_widget.day_choices(fmt)

        formats = ['Y', 'y', None]
        for fmt in formats:
            date_widget.year_choices(fmt)

    def test_core(self):
        """
        Only checks parts that are not covered by other Remote Care tests
        """
        self.check_forms()
        self.check_models()
        self.check_widgets()
