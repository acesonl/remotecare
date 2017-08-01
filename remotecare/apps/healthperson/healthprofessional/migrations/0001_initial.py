# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-23 21:54
from __future__ import unicode_literals

import core.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('healthperson', '0001_initial'),
        ('secretariat', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='HealthProfessional',
            fields=[
                ('healthperson_ptr',
                 models.OneToOneField(auto_created=True,
                                      on_delete=django.db.models.deletion.CASCADE,
                                      parent_link=True,
                                      primary_key=True,
                                      serialize=False,
                                      to='healthperson.HealthPerson')),
                ('photo_location',
                 core.models.ImageField(blank=True,
                                        max_length=128,
                                        null=True,
                                        upload_to=b'upload',
                                        verbose_name='Pasfoto')),
                ('function',
                 models.CharField(choices=[(b'specialist',
                                            'Medisch specialist'),
                                           (b'assistant',
                                            'Arts-assistent'),
                                           (b'specializednurse',
                                            'Gespecialiseerd verpleegkundige'),
                                           (b'nurse',
                                            'Verpleegkundige'),
                                           (b'dietician',
                                            'Dietist')],
                                  max_length=128,
                                  verbose_name='Functie')),
                ('specialism',
                 models.CharField(choices=[(b'gastro_liver_disease',
                                            'Maag-darm-leverziekten'),
                                           (b'rheumatology',
                                            'Reumatologie'),
                                           (b'surgery',
                                            'Chirurgie'),
                                           (b'internal_medicine',
                                            'Interne geneeskunde'),
                                           (b'orhopedie',
                                            'Orhopedie')],
                                  max_length=128,
                                  verbose_name='Specialisme')),
                ('telephone',
                 models.CharField(max_length=256,
                                  verbose_name='Telefoonnummer contact polikliniek')),
                (
                    'urgent_control_notification',
                    models.CharField(
                        choices=[
                            (b'sms_and_email',
                             'Zowel per e-mail als per sms'),
                            (b'sms_only',
                             'Alleen per sms'),
                            (b'email_only',
                             'Alleen per e-mail'),
                            (b'to_secretary',
                             'Doorsturen naar')],
                        default=b'sms_and_email',
                        max_length=32,
                        verbose_name='Langer dan 3 dagen niet gereageerdop een urgente patient.')),
                ('out_of_office_start',
                 core.models.DateField(blank=True,
                                       null=True,
                                       verbose_name='Start datum afwezigheid')),
                ('out_of_office_end',
                 core.models.DateField(blank=True,
                                       null=True,
                                       verbose_name='Eind datum afwezigheid')),
                ('out_of_office_replacement',
                 models.ForeignKey(blank=True,
                                   null=True,
                                   on_delete=django.db.models.deletion.CASCADE,
                                   related_name='replacement_set',
                                   to='healthprofessional.HealthProfessional',
                                   verbose_name='Vervangende specialist tijdens afwezigheid')),
                ('urgent_control_secretary',
                 models.ForeignKey(blank=True,
                                   null=True,
                                   on_delete=django.db.models.deletion.CASCADE,
                                   to='secretariat.Secretary',
                                   verbose_name='Secretariaat medewerker')),
            ],
            options={
                'abstract': False,
            },
            bases=(
                'healthperson.healthperson',
                models.Model,
                core.models.ModelAuditMixin),
        ),
    ]