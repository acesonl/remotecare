# -*- coding: utf-8 -*-
"""
Standard baseclass form definitions & some widget definitions

:subtitle:`Class definitions:`
"""
import magic
import datetime
from django.conf import settings
from django import forms
from core.widgets import SelectDateWidget
from django.forms.widgets import Select, RadioSelect
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat


class InnerQuerySet(object):
    objects = []
    _prefetch_related_lookups = False

    def __init__(self, objects):
        self.objects = objects

    def __iter__(self):
        return iter(self.objects)

    def iterator(self):
        return iter(self.objects)

    def objects(self):
        return self.iterator()


class QuerysetWrapper(object):
    """
    Queryset wrapper for caching the choices coupled to a
    ManyToManyField. The querysetwrapper provides functions
    which otherwise should be called on the queryset directly.

    Dramatically reduces the amount of queries needed when rendering
    form fieldsets via a fieldset template.
    """

    _prefetch_related_lookups = False
    inner_queryset = None

    def __init__(self, objects):
        """
        Store the objects in the wrapper
        """
        self.inner_queryset = InnerQuerySet(objects)

    def __iter__(self):
        return iter(self.inner_queryset.objects)

    def all(self):
        """
        Returns:
            All stored objects
        """
        return self.inner_queryset

    def objects(self):
        return self.inner_queryset.objects()

    def __len__(self):
        """
        Returns:
            The length of the stored objects
        """
        return len(self.inner_queryset.objects)

    def none(self):
        """
        Returns:
            An empty list
        """
        return []

    def filter(self, **kwargs):
        """
        Filter function which accepts pk and pk__in
        filters.

        Returns:
            A list of objects
        """
        if 'pk' in kwargs:
            for obj in self.inner_queryset.objects:
                if str(obj.pk) == kwargs['pk']:
                    return [obj]

        if 'pk__in' in kwargs:
            obj_list = []
            for obj in self.inner_queryset.objects:
                if str(obj.pk) in kwargs['pk__in']:
                    obj_list.append(obj)
            return obj_list

        raise Exception('The used filter cannot be found: ' + str(kwargs))


class BaseClassForm(object):
    '''
    Base class form which holds the functions shared among
    all forms. Automatically adds placeholders
    '''
    def add_placeholders_to_fields(self):
        '''
        Automatically add the 'placeholder' attribute
        to appropiate HTML input elements
        '''
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                # Only do this for textinput, dateinput and emailinput
                if ((type(field.widget) in
                     (forms.TextInput, forms.DateInput, forms.EmailInput))):
                    field.widget = forms.TextInput(
                        attrs={'placeholder': field.label})

    def get_fields(self):
        """
        Returns:
            array of all the fields in the fieldset definition
            for form param
        """
        # Get the fields of a form
        fields = []
        for fieldset in self.fieldsets():
            fields += fieldset[1]
        return fields

    def fieldsets(self):
        '''
        Instead of using fields on forms, fieldsets are used.
        This allows ordening the fields in sets and
        hiding/showing different sets based on selected values
        '''
        if hasattr(self, 'Meta'):
            fieldsets = getattr(self.Meta, 'fieldsets', None)
        else:
            fieldsets = None

        if not hasattr(self, 'form_fieldsets'):
            if fieldsets:
                fs = []
                for name, fieldset in fieldsets:
                    fs.append(
                        (name, [self[field] for field in fieldset['fields']]))
                self.form_fieldsets = fs
            else:
                self.form_fieldsets = [(None, [field for field in self])]
        return self.form_fieldsets

    def queryset_speed_up(self):
        """
        Dramatically decreases the amount of queries necessary
        in template rendering of ManyToManyFields by replacing
        the queryset with a :class:`QuerysetWrapper` instance.

        If not replaced, every time the (BoundField)
        'field' variable is used in the template the choices
        are retrieved from the database, resulting in some cases
        in 40+ queries.

        Execute this function in the __init__ of forms that have
        one or more instances of :class:`ModelMultipleChoiceField`
        """
        if hasattr(self, 'Meta'):
            fieldsets = getattr(self.Meta, 'fieldsets', None)
        else:
            fieldsets = None

        # Replace the queryset with the wrapper
        # for ModelMultipleChoiceField
        # Avoiding many database hits when creating
        # BoundFields for this instance
        for name, fieldset in fieldsets:
            for field_name in fieldset['fields']:
                if ((isinstance(self.fields[field_name],
                     ModelMultipleChoiceField))):
                    self.fields[field_name].queryset =\
                        QuerysetWrapper(
                            [x for x in self.fields[field_name].queryset])


class BaseForm(forms.Form, BaseClassForm):
    '''
    Baseclass form which is based on forms.Form
    '''
    def __init__(self, *args, **kwargs):
        # pop the changed_by_user for audit trailing
        self.changed_by_user = kwargs.pop('changed_by_user', None)
        super(BaseForm, self).__init__(*args, **kwargs)
        self.add_placeholders_to_fields()

    def save(self, *args, **kwargs):
        # auto add the changed_by_user to the instance
        instance = super(BaseForm, self).save(*args, **kwargs)
        instance.changed_by_user = self.changed_by_user
        return instance


class BaseModelForm(forms.ModelForm, BaseClassForm):
    '''
    Baseclass form which is based on forms.ModelForm
    '''
    def __init__(self, *args, **kwargs):
        # pop the changed_by_user for audit trailing
        self.changed_by_user = kwargs.pop('changed_by_user', None)
        super(BaseModelForm, self).__init__(*args, **kwargs)
        self.add_placeholders_to_fields()

    def save(self, *args, **kwargs):
        # auto add the changed_by_user to the instance
        instance = super(BaseModelForm, self).save(*args, **kwargs)
        instance.changed_by_user = self.changed_by_user
        return instance


class DisplayWidget(forms.Widget):
    '''
    Widget for displaying values
    '''
    def render(self, name, value, attrs=None):
        return mark_safe(value)

    def clean(self, value):
        return value


class ImageField(forms.ImageField):
    """
    Override ImageField to allow setting a maximum
    upload size and checking mime_type with help of
    the 'magic' package.
    """

    def __init__(self, *args, **kwargs):
        self.max_upload_size = kwargs.pop('max_upload_size', None)
        if not self.max_upload_size:
            self.max_upload_size = settings.MAX_UPLOAD_SIZE
        super(ImageField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ImageField, self).clean(*args, **kwargs)

        if data:
            try:
                if data.size > self.max_upload_size:
                    raise forms.ValidationError(
                        _('Afbeelding moet kleiner zijn dan %s.' +
                          'Huidige grootte is %s.')
                        % (filesizeformat(self.max_upload_size),
                           filesizeformat(data.size)))
            except AttributeError:
                pass
            # Check if 'image' is in mime_type
            mime_type = magic.from_buffer(data.read(1024), mime=True)
            if 'image' not in mime_type:
                raise forms.ValidationError(
                    _('Het geuploade bestand kan niet worden herkend' +
                      ' als afbeelding'))
            data.seek(0)

        return data


class MultipleChoiceField(forms.MultipleChoiceField):
    '''
    Django formfield for multiple selections
    '''
    widget = forms.CheckboxSelectMultiple


class ModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    '''
    Django formfield for multiple selections
    '''
    widget = forms.CheckboxSelectMultiple


class ChoiceOtherWidget(forms.MultiWidget):
    '''
    Django widget for choice other fields

    Displays a select box  with the option for 'other' allowing
    to specify a value via a textinput
    '''
    def __init__(self, choices, other_field, maxlength=128, attrs=None):

        widgets = [
            forms.Select(
                choices=choices,
                attrs={'class': 'other-choice-select'}),
            other_field(
                attrs={
                    'class': 'other-choice-text',
                    'rows': 3, 'maxlength': maxlength
                })]

        super(ChoiceOtherWidget, self).__init__(widgets, attrs)

    def choices(self):
        '''
        Returns:
            The widget choices
        '''
        return self.widgets[0].choices

    def decompress(self, value):
        '''
        Returns:
            an array with the value or ['other', value]
        '''
        if value in ('', None):
            return ['', '']
        if value not in [i[0] for i in self.widgets[0].choices]:
            return ['other', value]
        return [value, '']

    def format_output(self, rendered_widgets):
        '''
        Returns:
            the rendered widgets seperated by a breakline
        '''
        return '<br />'.join(rendered_widgets)


class ChoiceOtherField(forms.MultiValueField):
    '''
    Django formfield for choice other fields
    '''
    def __init__(self, choices=[], *args, **kwargs):
        self._select_required = kwargs.pop('required', True)
        self.other_field = kwargs.pop('other_field')
        self.maxlength = kwargs.pop('maxlength', 128)
        self.choices = choices
        fields = [forms.TypedChoiceField(choices=choices), forms.CharField()]

        widget = ChoiceOtherWidget(
            choices=choices,
            other_field=self.other_field,
            maxlength=self.maxlength
        )

        if not self._select_required:
            kwargs.update({'required': False})
        super(ChoiceOtherField, self).__init__(
            fields=fields, widget=widget, **kwargs)

    def fix_value_from_post(self, post_data, field_name):
        '''
        Used for fixing post data so it can be
        temporarily stored in the database and later
        used as form initial data
        '''
        value = self.get_value_from_post(post_data, field_name)
        post_data[field_name] = value

        select_name = field_name + '_0'
        text_name = field_name + '_1'

        if select_name in post_data:
            del post_data[select_name]
        if text_name in post_data:
            del post_data[text_name]

    def get_value_from_post(self, post_data, field_name):
        '''
        Get the value from the dropbox except when 'other' is selected
        if 'other' use the value from the textinput
        '''
        rt = None
        select_name = field_name + '_0'
        text_name = field_name + '_1'
        if select_name in post_data:
            try:
                select_value = post_data[select_name]
                if select_value == 'other':
                    if text_name in post_data:
                        rt = post_data[text_name]
                else:
                    rt = select_value
            except KeyError:
                rt = None
        return rt

    def clean(self, value):
        '''
        Raise error messages if needed
        '''
        if value[0] in (None, '') and self._select_required:
            raise forms.ValidationError(self.error_messages['required'])
        if ((value[0] == 'other' and value[1] in (None, '') and
             self._select_required)):
            raise forms.ValidationError(self.error_messages['required'])

        if value[0] != 'other':
            value = value[0]
        else:
            value = super(ChoiceOtherField, self).clean(value)
        return value

    def compress(self, data_list):
        '''
        data_list is a list of two items. The first item is the value from
        the TypeChoiceField and the second one is from the text input.
        '''
        if not data_list:
            return ''
        if data_list[0] == 'other' and data_list[1] != '':
            return data_list[1]

        return data_list[0]


#class HorizontalRadioSelectRenderer(forms.RadioSelect.renderer):
#    '''
#    Django renderer, overrides widget method to put radio
#    buttons horizontally
#    instead of vertically.
#    '''
#    def render(self):  # pragma: no cover
#        '''Outputs radios'''
#        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class FormRadioSelect(RadioSelect):
    '''
    Django formfield which overrides the radio select field
    '''
    template_name = 'horizontal_select.html'

    # def __init__(self, *args, **kwargs):  # pragma: no cover
    #   super(FormRadioSelect, self).__init__(*args, **kwargs)
    #   # self.renderer = HorizontalRadioSelectRenderer


class SelectDateWidgetCustom(SelectDateWidget):
    '''
    Base class for SelectDateWidget, SelectDateTimeWidget and
    SelectTimeWidget.
    '''
    def render(self, name, value, attrs=None):
        '''
        Return the html code of the widget.
        '''
        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name
        local_attrs = self.build_attrs(self.attrs)
        self.values = self.parse_value(value)
        output = []
        index = 0
        for (n, fmt) in self.format:
            select_name = '%s_%s' % (name, n)
            local_attrs['id'] = '%s_%s' % (id_, n)
            if hasattr(self, '%s_choices' % n):
                choices = getattr(self, '%s_choices' % n)(fmt)
                if not self.required or not self.values[n]:
                    choices.insert(0, (-1, '---'))
                select = Select(choices=choices)
                attrs = local_attrs.copy()
                if attrs['class']:
                    attrs['class'] = attrs['class'] + '_' + n
                html = select.render(select_name, self.values[n], attrs)
                index = index + 1
                output.append(html)
        return mark_safe(u'\n'.join(output))


class DateWidget(SelectDateWidgetCustom):
    '''
    Django Widget for selecting dates
    '''
    def render(self, name, value, attrs=None):
        '''
        Render datewidget
        '''
        output = super(DateWidget, self).render(name, value, attrs)
        return mark_safe(output + ' <span class="date_field"></span>')


class FormDateField(forms.DateField):
    '''
    Django Formfield for dates
    '''
    widget = DateWidget

    def __init__(self, *args, **kwargs):
        self.allow_future_date = kwargs.pop('allow_future_date', True)
        self.allow_before_birth_date = kwargs.pop(
            'allow_before_birth_date', True)
        self.allow_after_deceased = kwargs.pop('allow_after_deceased', False)
        self.future = kwargs.pop('future', False)
        self.years = kwargs.pop('years', None)
        super(FormDateField, self).__init__(*args, **kwargs)
        if self.years:
            self.widget.years = self.years
        self.widget.required = self.required

    def fix_value_from_post(self, post_data, field_name):
        '''
        Used for fixing post data so it can be
        temporarily stored in the database and later
        used as form initial data
        '''
        value = self.get_value_from_post(post_data, field_name)
        post_data[field_name] = value

        day_name = field_name + '_day'
        month_name = field_name + '_month'
        year_name = field_name + '_year'

        if day_name in post_data:
            del post_data[day_name]
        if month_name in post_data:
            del post_data[month_name]
        if year_name in post_data:
            del post_data[year_name]

    def get_value_from_post(self, post_data, field_name):
        '''
        Try to get the value from post_data, used to temporarily
        store the value.
        '''
        rt = None
        day_name = field_name + '_day'
        month_name = field_name + '_month'
        year_name = field_name + '_year'

        if ((day_name in post_data and
             month_name in post_data and year_name in post_data)):
            try:
                day = int(post_data[day_name])
                month = int(post_data[month_name])
                year = int(post_data[year_name])
                rt = datetime.date(year, month, day)
            except ValueError:
                rt = None
        return rt

    def clean(self, value):
        '''
        Date validation checks
        '''
        value = super(FormDateField, self).clean(value)
        if not self.allow_future_date and value not in (None, ''):
            if datetime.date.today() < value:
                raise forms.ValidationError(
                    _(u'Datum mag niet in de toekomst liggen.'))
        if self.future and value not in (None, ''):
            if datetime.date.today() > value:
                raise forms.ValidationError(
                    _(u'Alleen toekomstige datum is geldig.'))

        return value

    def widget_attrs(self, widget):
        '''
        Add datefield CSS class by default
        '''
        attrs = super(FormDateField, self).widget_attrs(widget)
        attrs.update({'class': 'datefield', })
        return attrs


NONE_YES_NO_CHOICES = (
    (1, '---------'),
    (2, 'Yes'),
    (3, 'No'),
)


class YesNoChoiceField(forms.NullBooleanField):
    '''
    Django formfield for yes/no selections
    '''
    widget = forms.NullBooleanSelect

    def __init__(self, *args, **kwargs):
        super(YesNoChoiceField, self).__init__(*args, **kwargs)
        self.widget.choices = NONE_YES_NO_CHOICES
