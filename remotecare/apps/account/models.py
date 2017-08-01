# -*- coding: utf-8 -*-
"""
This module contains the User model and other models
for storing login attempts, a list of old hashed
passwords, password change request and temporarily
storages of the (hashed) login sms code.

An user is coupled to one of the 4 different possible roles in Remote Care:
    - Patient
    - Healthprofessional
    - Secretary
    - Manager

Via the polymorphicmodel: :class:`apps.healthperson.models.HealthPerson` as can
be seen in the next model relationship diagram:

.. graphviz:: ../../_static/user_healthperson.dot

All personal user data is stored encrypted and, if searchable, also hashed.
This key for encryption/decryption is the encryption_key of the user
which is encrypted/decrypted with the MASTER_KEY in the settings file.
The hashes are in HMAC format. The HMAC secrets are stored in the settings
file.

Users are hospital 'bound' meaning that an healthprofessional/secretary
can only find patients within the same hospital during searching.

:subtitle:`Class definitions:`
"""
from django.core.cache import cache
from datetime import date, timedelta, datetime
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser,\
    BaseUserManager, PermissionsMixin
from core.models import DateField, YesNoChoiceField,\
    EncryptedHMACLookupCharField, EncryptedHMACLookupEmailField,\
    EncryptedCharField, AuditBaseModel
from django.utils.translation import ugettext as _
from apps.rcmessages.models import RCMessage
from apps.lists.models import Hospital
from apps.questionnaire.models import QuestionnaireRequest
from apps.healthperson.models import HealthPerson
from django.utils.functional import cached_property

GENDER_CHOICES = (
    ('male', ('Man')),
    ('female', ('Vrouw')),
)

TITLE_CHOICES = (
    ('mr', ('Dhr.')),
    ('ms', ('Mevr.')),
    ('dr', ('Dr.')),
    ('prof', ('Prof.')),
)


class UserManager(BaseUserManager):  # pragma: no cover
    '''
    Custom user manager which allows adding an user via
    the manage.py command using email as unique key and
    filling in other required information
    '''
    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        note: encrypted_email is not encrypted yet here, will be encrypted
        when the user is saved.
        """
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Creates and saves a super user with the same parameters as
        create_user
        """
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class EncryptionKey(models.Model):
    """
    Stores all encryption keys
    of the users.

    Encrypts/decrypts them with the MASTER_KEY setting.
    """
    # use lambda notation for encryption_key setting
    key = EncryptedCharField(
        max_length=256,
        encryption_key=lambda: settings.MASTER_KEY)

    @classmethod
    def update_cached_keys(cls):
        queryset = cls.objects.select_related('user').all()

        if settings.AUTOMATIC_TESTING:
            # During loading fixtures the users are not
            # loaded yet
            cache.set('encryption_keys',
                      dict(queryset.values_list('id', 'key')))
        else:
            if [True for x,y in queryset.values_list('user', 'key') if x is None]:
                cache.set('encryption_keys',
                          dict(queryset.values_list('id', 'key')))
            else:
                cache.set('encryption_keys',
                          dict(queryset.values_list('user', 'key')))


    @classmethod
    def get_with_user_id(cls, user_id):
        if 'encryption_keys' not in cache:
            cls.update_cached_keys()
        cached_keys = cache.get('encryption_keys')
        if user_id not in cached_keys:
            cls.update_cached_keys()
            cached_keys = cache.get('encryption_keys')
        return cached_keys[user_id]

    @classmethod
    def update_cached_healthperson_ids(cls):
        from apps.healthperson.models import HealthPerson
        queryset = HealthPerson.objects.select_related('user').all()
        cache.set('healthperson_ids',
                  dict(queryset.values_list('id', 'user')))

    @classmethod
    def get_with_healthperson_id(cls, healthperson_id):
        if 'healthperson_ids' not in cache:
            cls.update_cached_healthperson_ids()

        cached_healthperson_ids = cache.get('healthperson_ids')
        if healthperson_id not in cached_healthperson_ids:
            cls.update_cached_healthperson_ids()
            cached_healthperson_ids = cache.get('healthperson_ids')

        user_id = cached_healthperson_ids[healthperson_id]

        return cls.get_with_user_id(user_id)


class User(AbstractBaseUser, PermissionsMixin, AuditBaseModel):
    '''
    Custom user model which saves basic information about the user.
    All private information is encrypted.

    Private information is stored encrypted in the database via
    encrypted model fields. See the :class:`core.models.EncryptBaseField`
    for more information on encryption.

    Private information that should also be searchable is represented by
    both an encrypted field and an HMAC field. See the
    :class:`core.models.EncryptLookupBaseField` for more information on
    encryption and HMAC lookup.
    '''

    # THIS SHOULD ALWAYS BE THE FIRST FIELD
    personal_encryption_key = models.OneToOneField(
        EncryptionKey)

    # : Encrypted first name
    # use lambda notation for passing the hmac_key setting
    first_name = EncryptedHMACLookupCharField(
        _('Voornaam'),
        max_length=128,
        hmac_key=lambda: settings.FIRSTNAME_SEARCH_KEY,
        encryption_key='encryption_key')

    last_name = EncryptedHMACLookupCharField(
        _('Achternaam'),
        max_length=128,
        hmac_key=lambda: settings.SURNAME_SEARCH_KEY,
        encryption_key='encryption_key')

    email = EncryptedHMACLookupEmailField(
        _('E-mail adres'),
        max_length=254,
        hmac_unique=True,
        hmac_key=lambda: settings.EMAIL_SEARCH_KEY,
        encryption_key='encryption_key')

    title = models.CharField(
        choices=TITLE_CHOICES,
        max_length=8,
        verbose_name=_('Titel'),
        null=True,
        blank=True)

    initials = models.CharField(
        max_length=32,
        verbose_name=_('Voorletters'),
        blank=True,
        null=True)

    prefix = models.CharField(
        max_length=32,
        verbose_name=_('Tussenvoegsel'),
        null=True,
        blank=True)

    # No search on mobile number, so no HMAC field
    mobile_number = EncryptedCharField(
        max_length=128,
        verbose_name=_('Mobiel telefoonnummer'),
        encryption_key='encryption_key')

    gender = models.CharField(
        choices=GENDER_CHOICES,
        max_length=128,
        verbose_name=_('Geslacht'))

    # Hospital of the user
    hospital = models.ForeignKey(
        Hospital,
        verbose_name=_('Ziekenhuis'),
        null=True,
        blank=True)

    # The local hospital number encrypted with HMAC lookup
    local_hospital_number = EncryptedHMACLookupCharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name=_('Lokaal ziekenhuis-nummer'),
        hmac_key=lambda: settings.HOSPITAL_NUMBER_SEARCH_KEY,
        encryption_key='encryption_key')

    # BSN encrypted field with HMAC lookup
    BSN = EncryptedHMACLookupCharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name=_('Burger Service Nummer'),
        hmac_key=lambda: settings.BSN_SEARCH_KEY,
        encryption_key='encryption_key')

    # Encrypt in a later stage?
    date_of_birth = DateField(
        verbose_name=_('Geboortedatum'),
        allow_future_date=False)

    # Link to the polymorphic HealthPerson which can be: Manager,
    # Patient, Secretary or HealthProfessional
    healthperson = models.OneToOneField(
        HealthPerson,
        blank=True,
        null=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now)

    account_blocked = YesNoChoiceField(
        blank=True,
        null=True)

    deleted_on = models.DateField(
        blank=True,
        null=True)

    objects = UserManager()

    USERNAME_FIELD = 'hmac_email'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name',
                       'mobile_number', 'date_of_birth']

    # Fields to ignore for the audit trail
    AUDIT_IGNORE_FIELDS = [
        'is_active', 'date_joined', 'is_staff', 'hmac_email', 'hmac_BSN',
        'hmac_last_name', 'hmac_email', 'account_blocked', 'deleted_on',
        'personal_encryption_key', 'hmac_local_hospital_number', 'last_login',
        'is_superuser', 'hmac_first_name',
        ]

    def in_group(self, group_name):
        if not hasattr(self, 'user_groups'):
            self.user_groups = [x.name for x in self.groups.all()]
        return group_name in self.user_groups

    @property
    def default_group(self):
        if not hasattr(self, 'user_groups'):
            self.user_groups = [x.name for x in self.groups.all()]
        return self.user_groups[0]

    @property
    def get_date_of_birth(self):
        return self.date_of_birth

    @property
    def new_questionnaire_request(self):
        """
        Returns true if the patient has no questionnaire requests
        """
        return not QuestionnaireRequest.objects.filter(
            patient=self.healthperson).count() == 0

    @property
    def new_message_count(self):
        """
        Returns the amount of unread messages
        """
        count = RCMessage.objects.filter(
            read_on__isnull=True, patient=self.healthperson).count()

        if count == 0:
            return 'no'
        return count

    @property
    def full_name(self):
        '''
        Returns the full_name of an user which is: first_name +
        prefix + last_name
        '''
        full_name = self.first_name

        if self.prefix:
            full_name += ' ' + self.prefix

        full_name += ' ' + self.last_name
        return full_name

    @property
    def professional_name(self):
        '''
        Returns the full_name of an user which is: initials +
        prefix + last_name
        '''
        if self.title:
            full_name = self.get_title_display() + ' ' + self.initials
        else:
            full_name = self.initials

        if self.prefix:
            full_name += ' ' + self.prefix
        full_name += ' ' + self.last_name
        return full_name

    @property
    def is_deleted(self):
        """
        Returns True if the user has been set for deletion.
        """
        return self.deleted_on is not None

    @property
    def audit_encryption_key_id(self):
        """
        Get the EncryptionKey id so it can be coupled to the log item
        in the audit.

        Returns:
            The id of the EncryptionKey that is used to encrypt the
            model instance.
        """
        return self.personal_encryption_key_id

    @cached_property
    def encryption_key(self):
        """
        Get the encryption key of the user.

        .. Note: Since this method is called during the initalization of
                 a couple of fields of a user instance, the
                 personal_encryption_key field needs to be the first field
                 on the model else the personal_encryption_key_id could
                 be not set.

        Returns:
            The encryption key of the user instance.
        """
        if not self.id:
            # If the id is not set searching for it in the
            # cache has no point.
            return self.personal_encryption_key.key

        encrypted_key = EncryptionKey.get_with_user_id(self.id)
        return EncryptionKey(key=encrypted_key).key

    def save(self, *args, **kwargs):
        if not self.last_login:
            self.last_login = datetime.now()
        super(User, self).save(*args, **kwargs)


class LoginAttempt(models.Model):
    '''
    Stores all login attempts for administration purposes.
    Login attempts with extra info and
    an hash of the username = email address
    '''
    succesfull = YesNoChoiceField()
    ipaddress = models.CharField(max_length=128, blank=True, null=True)
    useragent = models.TextField(blank=True, null=True)
    extra_info = models.TextField(blank=True, null=True)
    session_id = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now=True)
    username_hash = models.TextField(blank=True, null=True)


class LoginSMSCode(models.Model):
    '''
    Temporarily stores the hmac_sms_code used during login
    '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    hmac_sms_code = models.CharField(max_length=256, blank=True, null=True)


class OldPassword(models.Model):
    '''
    Stores previous passwords and the current password.
    Can both be used to validate that the password is different from the
    # last passwords
    and check if the password is expired.
    '''
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='old_passwords')
    password_hash = models.CharField(max_length=128)
    date_added = DateField(auto_now=True)


class PasswordChangeRequest(models.Model):
    '''
    Temporarly stores the sms_code and key for resetting the password.
    Email and sms HMAC thus when set only can check using HMAC secret.
    The attempt_nr field is used to limit the total amount of attempts
    possible.
    '''
    # Search keys & checks. (system only stores hmacs to verify, raw
    # keys are not stored)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='password_change_requests')
    hmac_email_key = models.CharField(max_length=256)
    hmac_sms_code = models.CharField(max_length=256, blank=True, null=True)
    added_on = DateField(auto_now=True)
    attempt_nr = models.IntegerField(blank=True, null=True)

    # expiry date is added_on + 1-2 days.
    # (since only based on date and not date + time)
    @property
    def expiry_date(self):
        return self.added_on + timedelta(days=2)

    @property
    def is_expired(self):
        return self.expiry_date <= date.today()


class AgreedwithRules(models.Model):
    '''
    Stores whether the user agreed with the rules for using Remotecare.
    '''
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=False)
    dateofagreement = models.DateTimeField(auto_now_add=True)
