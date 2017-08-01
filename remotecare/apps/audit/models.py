# -*- coding: utf-8 -*-
import json
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.account.models import EncryptionKey
from django.core.serializers.json import DjangoJSONEncoder
from core.encryption.symmetric import decrypt, is_encrypted


class LogEntry(models.Model):
    """
    Stores a change to a model instance in json format.
    """
    # Date and time of the change
    added_on = models.DateTimeField(
        default=timezone.now)

    # User that performed the change
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL)

    # optionally store a link to the encryption_key
    encryption_key = models.ForeignKey(
        EncryptionKey,
        null=True,
        blank=True)

    # Stored changes including the module, model_name and model_id
    # optionally encrypted
    json = models.TextField(
        null=True,
        blank=True)

    def update_changes(self, update_dict):
        audit_values = self.get_changes(do_decrypt=False)
        audit_values.update(update_dict)
        self.set_changes(audit_values)

    def get_changes(self, do_decrypt=True):
        audit_values = json.loads(
            self.json, cls=json.JSONDecoder)

        if do_decrypt and self.encryption_key is not None:
            decrypt_key = self.encryption_key.key

            changes = audit_values['changes']
            for key in changes:
                value = changes[key]
                if ((type(value) in (unicode, str) and
                     is_encrypted(changes[key]))):
                    changes[key] = decrypt(str(changes[key]),
                                           str(decrypt_key))
            audit_values['changes'] = changes
        return audit_values

    def set_changes(self, audit_values):
        encoder = DjangoJSONEncoder(separators=(',', ':'))
        self.json = encoder.encode(audit_values)
