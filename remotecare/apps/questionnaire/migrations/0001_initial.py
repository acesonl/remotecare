# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-23 21:54
from __future__ import unicode_literals

import core.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('secretariat', '0001_initial'),
        ('patient', '0001_initial'),
        ('healthprofessional', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionnaireRequest',
            fields=[
                ('id',
                 models.AutoField(auto_created=True,
                                  primary_key=True,
                                  serialize=False,
                                  verbose_name='ID')),
                ('urgent', models.BooleanField(default=False)),
                ('deadline_nr', models.IntegerField(blank=True, null=True)),
                ('deadline',
                 core.models.DateField(blank=True,
                                       null=True,
                                       verbose_name='Deadline')),
                ('created_on', models.DateField(auto_now_add=True)),
                ('finished_on', models.DateField(blank=True, null=True)),
                ('read_on', models.DateField(blank=True, null=True)),
                ('patient_diagnose',
                 models.CharField(choices=[(b'rheumatoid_arthritis',
                                            b'Reumatoide artritis'),
                                           (b'chron',
                                            b'Ziekte van Crohn'),
                                           (b'colitis_ulcerosa',
                                            b'Colitis Ulcerosa'),
                                           (b'intestinal_transplantation',
                                            b'Dunnedarmtransplantatie')],
                                  max_length=128,
                                  verbose_name='Diagnose')),
                ('saved_finish_later', models.BooleanField(default=False)),
                ('last_filled_in_step',
                 models.CharField(blank=True,
                                  max_length=4,
                                  null=True)),
                ('last_filled_in_form_step',
                 models.CharField(blank=True,
                                  max_length=4,
                                  null=True)),
                ('handled_on', models.DateField(blank=True, null=True)),
                ('appointment_needed', models.BooleanField(default=False)),
                ('appointment_added_on',
                 models.DateField(blank=True, null=True)),
                ('appointment_added_by',
                 models.ForeignKey(blank=True,
                                   null=True,
                                   on_delete=django.db.models.deletion.CASCADE,
                                   to='secretariat.Secretary')),
                ('handled_by',
                 models.ForeignKey(blank=True,
                                   null=True,
                                   on_delete=django.db.models.deletion.CASCADE,
                                   related_name='handled_by',
                                   to='healthprofessional.HealthProfessional')),
                ('patient',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='patient.Patient')),
                ('practitioner',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='healthprofessional.HealthProfessional')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, core.models.ModelAuditMixin),
        ),
        migrations.CreateModel(
            name='RequestStep',
            fields=[
                ('id',
                 models.AutoField(auto_created=True,
                                  primary_key=True,
                                  serialize=False,
                                  verbose_name='ID')),
                ('step_nr', models.IntegerField()),
                (
                    'model',
                    models.CharField(
                        choices=[
                            (b'StartQuestionnaire',
                             '001 Hoe gaat het met u?'),
                            (b'IBDQuestionnaire',
                             '002 Ziekteactiviteit - Ziekte van Chron en Colitis Ulcerosa'),
                            (b'RADAIQuestionnaire',
                             '003 Ziekteactiviteit - Rheumatoide artritis - RADAI vragenlijst'),
                            (b'QOLChronCUQuestionnaire',
                             '004 Kwaliteit van het leven - Ziekte van Chron en Colitis Ulcerosa (deel lastmeter)'),
                            (b'QOLQuestionnaire',
                             '005 Kwaliteit van het leven - Dunnedarmtransplantatie (lastmeter)'),
                            (b'RheumatismSF36',
                             '006 Kwaliteit van het leven - SF36 Reumatoide artritis'),
                            (b'QOHCQuestionnaire',
                             '007 Kwaliteit van zorg vragenlijst'),
                            (b'FinishQuestionnaire',
                             '008 Afspraak, bloedprikken en afsluiting'),
                            (b'StartUrgentQuestionnaire',
                             '009 Direct een afspraak'),
                            (b'UrgentProblemQuestionnaire',
                             '010 Omschrijving problemen')],
                        max_length=256,
                        verbose_name='Kies vragenlijst')),
                ('questionnairerequest',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='questionnaire.QuestionnaireRequest')),
            ],
        ),
        migrations.CreateModel(
            name='WizardDatabaseStorage',
            fields=[
                ('id',
                 models.AutoField(auto_created=True,
                                  primary_key=True,
                                  serialize=False,
                                  verbose_name='ID')),
                ('data', models.TextField(blank=True, null=True)),
                ('created_on', models.DateField(auto_now_add=True)),
                ('questionnaire_request',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                   to='questionnaire.QuestionnaireRequest')),
            ],
        ),
    ]
