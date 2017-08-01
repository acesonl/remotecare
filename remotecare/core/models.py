# -*- coding: utf-8 -*-
"""
Includes ModelField definitions.

:subtitle:`Class definitions:`
"""
import logging
from datetime import date
from django.db import models
from core.encryption.symmetric import encrypt, decrypt,\
    get_max_length, is_encrypted as is_encrypted_func
from django.conf import settings
from django import forms
from django.forms.models import model_to_dict
from core.forms import DateField as forms_DateField
from core.forms import YesNoChoiceField as forms_YesNoChoiceField,\
    FormRadioSelect as forms_RadioSelect,\
    ChoiceOtherField as forms_ChoiceOtherField,\
    ModelMultipleChoiceField as forms_ModelMultipleChoiceField,\
    ImageField as forms_ImageField
from core.encryption.hash import create_hmac as do_create_hmac
from django.utils.six import with_metaclass

logger = logging.getLogger(__name__)


class ManyToManyField(models.ManyToManyField):
    '''
    Django modelfield for storing many to many relations
    updates the form_class
    '''
    def __init__(self, *args, **kwargs):
        super(ManyToManyField, self).__init__(*args, **kwargs)
        self.help_text = ''

    def formfield(self, **kwargs):
        """
        Update the formfield
        """
        defaults = {'form_class': forms_ModelMultipleChoiceField}
        defaults.update(kwargs)
        return super(ManyToManyField, self).formfield(**defaults)


class ChoiceOtherField(models.CharField):
    '''
    Django modelfield for allowing to choose from a selectbox or specify
    an other value
    '''
    def __init__(self, other_field=forms.TextInput, *args, **kwargs):
        """__init__(self,other_field=forms.TextInput,*args,**kwargs)"""
        self.other_field = other_field
        self.maxlength = kwargs.get('maxlength', 128)
        super(ChoiceOtherField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        """
        Update the formfield
        """
        if self.choices:
            defaults = {'required': not self.blank,
                        'label': self.verbose_name,
                        'help_text': self.help_text,
                        'other_field': self.other_field,
                        'maxlength': self.maxlength}
            defaults.update(**kwargs)
            return forms_ChoiceOtherField(
                choices=self.get_choices(), **defaults)
        else:
            return super(ChoiceOtherField, self).formfield(**kwargs)

    def clean(self, value, model_instance):
        return value


class CheckBoxIntegerField(models.IntegerField):
    '''
    Integerfield with checkbox as widget
    '''
    def __init__(self, *args, **kwargs):
        self.formnr = kwargs.pop('form', None)
        default = {
            'default': None,
        }
        kwargs.update(**default)
        super(CheckBoxIntegerField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        """
        Update the formfield
        """
        if not kwargs.get('widget', None):
            default = {
                'widget': forms_RadioSelect,
            }
            kwargs.update(**default)
        rt = super(CheckBoxIntegerField, self).formfield(**kwargs)

        return rt


class CheckBoxCharField(models.CharField):
    '''
    Charfield with checkbox as widget
    '''
    def __init__(self, *args, **kwargs):
        self.formnr = kwargs.pop('form', None)
        default = {
            'default': None,
        }
        kwargs.update(**default)
        super(CheckBoxCharField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        """
        Update the formfield
        """
        if not kwargs.get('widget', None):
            default = {
                'widget': forms_RadioSelect,
            }

            kwargs.update(**default)
        return super(CheckBoxCharField, self).formfield(**kwargs)


class DateField(models.DateField):
    '''
    Django modelfield for storing dates
    '''
    def __init__(self, *args, **kwargs):
        self.allow_future_date = kwargs.pop('allow_future_date', True)
        self.allow_before_birth_date =\
            kwargs.pop('allow_before_birth_date', True)
        self.allow_after_deceased = kwargs.pop('allow_after_deceased', False)
        self.future = kwargs.pop('future', False)

        if self.future:
            self.years = kwargs.pop(
                'years',
                list(range(date.today().year, date.today().year + 10))
            )
        else:
            if self.allow_future_date:
                self.years = kwargs.pop(
                    'years',
                    list(range(date.today().year - 100,
                         date.today().year + 10))
                )
            else:
                self.years = kwargs.pop(
                    'years',
                    list(range(date.today().year - 100,
                         date.today().year + 1))
                )

        super(DateField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """
        Remove the time part of the datetime in case unicode or string
        is given as value
        """
        if isinstance(value, str) or isinstance(value, unicode):
            value_split = str(value).split(' ')
            if len(value_split) > 1:
                value = value_split[0]
        rt = super(DateField, self).to_python(value)

        return rt

    def formfield(self, **kwargs):
        """
        Update the formfield
        """
        defaults = {
            'form_class': forms_DateField,
            'allow_future_date': self.allow_future_date,
            'allow_before_birth_date': self.allow_before_birth_date,
            'allow_after_deceased': self.allow_after_deceased,
            'future': self.future,
            'years': self.years
        }
        defaults.update(**kwargs)
        return super(DateField, self).formfield(**defaults)


class ImageField(models.ImageField):
    '''
    Imagefield with maximum size validation
    '''
    def formfield(self, **kwargs):
        """
        Update the formfield
        """
        default = {
            'form_class': forms_ImageField,
        }
        kwargs.update(**default)
        return super(ImageField, self).formfield(**kwargs)


class YesNoChoiceField(models.NullBooleanField):
    '''
    Django modelfield for storing yes/no choices
    '''
    def formfield(self, **kwargs):
        """
        Update the formfield
        """
        default = {
            'form_class': forms_YesNoChoiceField,
        }
        kwargs.update(**default)
        return super(YesNoChoiceField, self).formfield(**kwargs)


def is_not_same(value, value2):
    if value is None and value2 == '':
        return True
    return value != value2


# Definitions for auditing models

class AuditUserNotDefinedError(Exception):
    """
    Error class for showing errors of not supported lookups
    """
    pass


class ModelAuditMixin(object):
    """
    A model mixin that tracks model fields' values and provide some useful
    functions to determine what fields have been changed.
    """
    DEFAULT_EXCLUDE_FIELDS = ['id']

    def __init__(self, *args, **kwargs):
        super(ModelAuditMixin, self).__init__(*args, **kwargs)

    def set_initial(self):
        self.__initial = self._dict

    @property
    def diff(self):
        initial = self.__initial
        current_values = self._dict
        diffs = [(name, (value, current_values[name])) for name, value in
                 initial.items() if is_not_same(value, current_values[name])]
        return dict(diffs)

    def remove_excluded_fields(self, fields, exclude_list):
        return_fields = {}
        for (field_name, field) in fields:
            if field_name not in exclude_list:
                return_fields.update({field_name: field})
        return return_fields

    def get_fields_values(self, field_names):
        values = {}
        # Return the pre_save value, so the values are automatically
        # encrypted
        for field_name in field_names:
            field = self.auditfields[field_name]
            value = field.pre_save(self, True)
            if isinstance(field, ImageField):
                try:
                    value = value.path
                except ValueError:
                    value = ''
            values.update({field_name: value})
        return values

    @property
    def auditfields(self):
        if not hasattr(self, 'cached_auditfields'):
            fields = [(field.name, field) for field in self._meta.fields]
            exclude_list = self.DEFAULT_EXCLUDE_FIELDS
            if hasattr(self, 'AUDIT_IGNORE_FIELDS'):
                exclude_list += self.AUDIT_IGNORE_FIELDS
            fields = self.remove_excluded_fields(fields, exclude_list)
            self.cached_auditfields = fields
        return self.cached_auditfields

    @property
    def _dict(self):
        return model_to_dict(self, self.auditfields.keys())

    def get_changed_by_user(self):
        user = None
        if not hasattr(self, 'changed_by_user'):
            if settings.DEBUG:
                # Raise an error when in debug modus.
                raise AuditUserNotDefinedError(
                    'Please use core.views.FormView as' +
                    ' baseclass and one of the two' +
                    ' baseclasses in core.forms')
            else:
                # Don't throw errors when in production,
                # instead pass it to the logger.
                logger.error(
                    'Please use core.views.FormView as' +
                    ' baseclass and one of the two' +
                    ' baseclasses in core.forms for model: ' +
                    self.__class__.__name__)
        else:
            user = self.changed_by_user
        return user

    def get_audit_entry(self, added=False):
        from apps.audit.models import LogEntry
        log_entry = None
        do_add_entry = True
        diff = None

        if not added:
            diff = self.diff
            if diff == {}:
                do_add_entry = False

        if do_add_entry:
            changed_by_user = self.get_changed_by_user()
            log_entry = LogEntry()

            if added:
                field_names = self.auditfields.keys()
            else:
                field_names = diff.keys()

            changes = self.get_fields_values(field_names)

            json_dict = {'module': self.__module__,
                         'name': self.__class__.__name__,
                         'id': self.id,
                         'changes': changes,
                         'added': added}
            log_entry.set_changes(json_dict)

            if changed_by_user is not None:
                if hasattr(self, 'audit_encryption_key_id'):
                    log_entry.encryption_key_id = self.audit_encryption_key_id
                log_entry.added_by_id = changed_by_user.id

        return log_entry


class AuditBaseModel(models.Model, ModelAuditMixin):
    """
    Basemodel which automatically
    generates audit trails for models.
    """
    def __init__(self, *args, **kwargs):
        super(AuditBaseModel, self).__init__(*args, **kwargs)
        if self.add_audit:
            self.set_initial()

    @property
    def add_audit(self):
        return not (settings.AUTOMATIC_TESTING and
                    settings.DISABLE_AUDITING_DURING_TEST)

    def save(self, **kwargs):
        """
        Override the save method to include
        the audit functions
        """
        log_entry = None
        old_id = self.id
        if self.add_audit:
            if not hasattr(self, 'disable_auditing'):
                log_entry = self.get_audit_entry(added=self.id is None)
                self.set_initial()
        super(AuditBaseModel, self).save(**kwargs)

        if self.add_audit and log_entry:
            if old_id is None:
                log_entry.update_changes({'id': self.id})
            if not log_entry.added_by_id:
                # In debug mode this raises an error,
                # but in production, save the json to the logger.
                logger.info(log_entry.json)
            else:
                log_entry.save()

    class Meta:
        abstract = True


# Definitions for encryption in models

class NotSupportedLookup(Exception):
    """
    Error class for showing errors of not supported lookups
    """
    def __init__(self, lookup):
        self.lookup = lookup

    def __str__(self):
        return "Lookup is not supported for EncryptTestField" % self.lookup


class SubfieldBase(type):
    """
    A metaclass for custom Field subclasses. This ensures the model's attribute
    has the descriptor protocol attached to it.
    """
    def __new__(cls, name, bases, attrs):
        new_class = super(SubfieldBase, cls).__new__(cls, name, bases, attrs)
        new_class.contribute_to_class = make_contrib(
            new_class, attrs.get('contribute_to_class')
        )
        return new_class


class Creator(object):
    """
    A placeholder class that provides a way to set the attribute on the model.
    """
    def __init__(self, field):
        self.field = field

    def __get__(self, obj, type=None):
        # obj = the model instance
        if obj is None:
            raise AttributeError('Can only be accessed via an instance.')
        return obj.__dict__[self.field.name]

    def __set__(self, obj, value):
        # obj = the model instance
        obj.__dict__[self.field.name] = self.field.to_python(value, obj)


def make_contrib(superclass, func=None):
    """
    Returns a suitable contribute_to_class() method for the Field subclass.

    If 'func' is passed in, it is the existing contribute_to_class() method on
    the subclass and it is called before anything else. It is assumed in this
    case that the existing contribute_to_class() calls all the necessary
    superclass methods.
    """
    def contribute_to_class(self, cls, name):
        if func:
            func(self, cls, name)
        else:
            super(superclass, self).contribute_to_class(cls, name)
        setattr(cls, self.name, Creator(self))

    return contribute_to_class


from django.db.models.lookups import Exact


class HMACExactLookup(Exact):
    def get_db_prep_lookup(self, value, connection):
        if value:
            value = self.lhs.field.create_hmac(value)
        return ('%s', [value])


class HMACField(models.CharField):
    """
    HMAC field which stores an HMAC version of the "associated_field"
    Automatically creates an HMAC hash when saving to the database
    and when looking up values in the database.
    """
    def __init__(self, *args, **kwargs):
        self.associated_field = kwargs.pop('associated_field', None)
        self.hmac_key = kwargs.pop('hmac_key', None)
        super(HMACField, self).__init__(*args, **kwargs)

    def create_hmac(self, value):
        """
        Shortcut function for generating a HMAC

        Args:
            - value: the value to generate a HMAC from

        Returns:
            The HMAC value
        """
        if isinstance(value, unicode):
            value = value.encode("utf8")
        return do_create_hmac(self.hmac_key(), str(value).lower())

    def pre_save(self, model_instance, add):
        """
        Called before saving to the database, automatically
        creates an HMAC of the value of the "associated_field"

        Args:
            - model_instance: the model_instance to use
            - add: newly added True/False

        Returns:
            The value to store in the database
        """
        value = getattr(model_instance, self.associated_field.attname)
        if value:
            return self.create_hmac(value)
        return value

    def get_db_prep_lookup_old(self, lookup_type, value, connection,
                           prepared=False):
        """
        Transform the lookup value in an HMAC. Only allow exact lookups.

        Args:
            - lookup_type: the name of the lookup
            - value: the lookup argument
            - connection: the database connection
            - prepared: is the value prepared to be used?

        Returns:
            The value to lookup in HMAC format.

        Raises:
            NotSupportedLookup if the lookup_type != exact.
        """
        if lookup_type == 'exact':
            if value:
                return [self.create_hmac(value)]
            return [value]
        raise NotSupportedLookup(lookup_type)

HMACField.register_lookup(HMACExactLookup)


class EncryptBaseField(with_metaclass(SubfieldBase)):
    """
    Base model field for encrypting the value before sending
    it to the database and decrypting it before storing it on
    a model instance.

    Provide a 'encryption_key' argument in the kwargs which is
    either a name of a property on the model instance or a function
    which returns the encryption_key.
    """
    def __init__(self, *args, **kwargs):
        max_length = kwargs.pop('max_length', None)
        if max_length:
            kwargs.update({'max_length': get_max_length(max_length)})
        self.encryption_key_func = kwargs.pop('encryption_key', None)
        super(EncryptBaseField, self).__init__(*args, **kwargs)

    def is_encrypted(self, value):
        """
        Check if the value is encrypted by comparing the first characters
        of the value to the list of known ciphers.

        Args:
            - value: the value to check (AES256CBC$#encrypted_value#)

        Returns:
            True if the cipher name could be found in the value else False
        """

        return is_encrypted_func(value)

    def encryption_key(self, model_instance):
        """
        Args:
            - obj: the model instance to get the 'self.encryption_key_func'
                   attribute of.

        Returns:
            The encryption/decryption key to use, either by using a property
            on a model instance or a function call.
        """
        if type(self.encryption_key_func) == str:
            # assume it is a property on the model instance
            if not model_instance:
                raise Exception('No instance given via' +
                                ' model_instance argument')
            return getattr(model_instance, self.encryption_key_func)
        else:
            # assume it is a function
            return self.encryption_key_func()

    def get_db_prep_value(self, value, connection, prepared):
        """
        Override this function so to_python does not get called
        before saving, which would lead to decrypting the value.
        """
        return value

    def to_python(self, value, model_instance=None):
        """
        Decrypts the value if it is encrypted

        Args:
            - value: The value to convert
            - model_instance: the model_instance the function is run for, or
              None

        Returns:
            The decrypted value if encrypted, else the value
        """
        if value and model_instance:
            if self.is_encrypted(value):
                return decrypt(str(value),
                               self.encryption_key(model_instance))

        # In case there is no obj or value
        # just return the value for None values and deserializing
        # objects in tests.
        # The last case means that the field is populated with encrypted data
        # however the pre_save method prevents double encryption.
        return value

    def pre_save(self, model_instance, add):
        """
        Encrypt the value if it is encrypted

        Args:
            - model_instance: the model_instance that is saved
            - add: newly added True/False

        Returns:
            The encrypted value to store.

        .. note:: getattr(model_instance, self.attname) calls
                  get_db_prep_value, which normally would call to_python.
                  But to store an encrypted value, this function is overriden.
        """
        value = getattr(model_instance, self.attname)
        if value:
            if not self.is_encrypted(value):
                value = encrypt(value, self.encryption_key(model_instance))
        return value


class EncryptLookupBaseField(EncryptBaseField):
    """
    Base modelfield combining both encryption and HMAC lookup.
    Automatically generates an hmac_#fieldname# modelfield on the model.

    Init the field with an "hmac_key" function
    (for example:  hmac_key=lambda:settings.HMAC_KEY)
    and the 'encryption_key' as used in the :class:`EncryptBaseField`.
    """
    def __init__(self, *args, **kwargs):
        # hmac_unique gets passed to the hmac field.
        self.hmac_key = kwargs.pop('hmac_key', None)
        self.hmac_unique = kwargs.pop('hmac_unique', False)
        super(EncryptLookupBaseField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        """
        Adds an extra hmac_#name# field to the model.
        """
        hmac_field = HMACField(
            max_length=128,
            blank=True,
            null=True,
            associated_field=self,
            hmac_key=self.hmac_key,
            unique=self.hmac_unique)
        # The creation counter needs to be reset else the field
        # will not be added at all.
        hmac_field.creation_counter = self.creation_counter
        # Default name = hmac_#field_name#
        cls.add_to_class('hmac_{0}'.format(name), hmac_field)

        # add the field as normal
        super(EncryptLookupBaseField, self).contribute_to_class(cls, name)

    def get_db_prep_lookup(self, lookup_type, value, connection,
                           prepared=False):
        """
        Don't search on encrypted fields!

        Raises:
            NotSupportedLookup
        """
        raise NotSupportedLookup(lookup_type)

# charfield, textfield and e-mail field versions of the EncryptedFields


class EncryptedHMACLookupCharField(EncryptLookupBaseField, models.CharField):
    """Encrypted charfield with HMAC lookup"""


class EncryptedHMACLookupTextField(EncryptLookupBaseField, models.TextField):
    """Encrypted textfield with HMAC lookup"""


class EncryptedHMACLookupEmailField(EncryptLookupBaseField, models.EmailField):
    """Encrypted emailfield with HMAC lookup"""


class EncryptedCharField(EncryptBaseField, models.CharField):
    """Encrypted charfield"""


class EncryptedTextField(EncryptBaseField, models.TextField):
    """Encrypted textfield"""


class EncryptedEmailField(EncryptBaseField, models.EmailField):
    """Encrypted emailfield"""
