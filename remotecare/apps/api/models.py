# -*- coding: utf-8 -*-
import os
import json
import binascii
from django.db import models
from core.models import EncryptedTextField
from django.conf import settings
from apps.healthperson.patient.models import Patient
from apps.healthperson.healthprofessional.models import HealthProfessional
from django.contrib.auth.models import AbstractBaseUser
from django.core.serializers.json import DjangoJSONEncoder


class APIUser(AbstractBaseUser):
    username = models.CharField(
        max_length=128)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username


class Token(models.Model):
    """
    The default authorization token model.
    """
    key = models.CharField(max_length=40, primary_key=True)
    user = models.OneToOneField(APIUser, related_name='auth_token')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Work around for a bug in Django:
        # https://code.djangoproject.com/ticket/19422
        #
        # Also see corresponding ticket:
        # https://github.com/tomchristie/django-rest-framework/issues/705
        abstract = 'rest_framework.authtoken' not in settings.INSTALLED_APPS

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key


class HealthProfessionalCoupling(models.Model):
    api_user = models.ForeignKey(APIUser)
    healthprofessional = models.OneToOneField(HealthProfessional)
    external_healthprofessional_id = models.CharField(
        max_length=128)
    extra_data = models.TextField(
        null=True,
        blank=True)


class PatientCoupling(models.Model):
    api_user = models.ForeignKey(APIUser)
    patient = models.OneToOneField(Patient)
    external_patient_id = models.CharField(
        max_length=128)
    extra_data = models.TextField(
        null=True,
        blank=True)


class TempPatientData(models.Model):
    """
    Temporary stores patient data which later
    can be used to create new patients
    """
    json_data = EncryptedTextField(
        null=True,
        blank=True,
        encryption_key='encryption_key')

    def get_json_data(self):
        return json.loads(self.json_data,
                          cls=json.JSONDecoder)

    def set_json_data(self, data):
        encoder = DjangoJSONEncoder(separators=(',', ':'))
        self.json_data = encoder.encode(data)

    @property
    def encryption_key(self):
        return settings.API_ENCRYPTION_KEY
