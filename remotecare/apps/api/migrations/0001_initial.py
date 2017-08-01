# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-07-13 22:59
from __future__ import unicode_literals

import core.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('patient', '0001_initial'),
        ('healthprofessional', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HealthProfessionalCoupling',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_healthprofessional_id', models.CharField(max_length=128)),
                ('extra_data', models.TextField(blank=True, null=True)),
                ('api_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.APIUser')),
                ('healthprofessional', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='healthprofessional.HealthProfessional')),
            ],
        ),
        migrations.CreateModel(
            name='PatientCoupling',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_patient_id', models.CharField(max_length=128)),
                ('extra_data', models.TextField(blank=True, null=True)),
                ('api_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.APIUser')),
                ('patient', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='patient.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='TempPatientData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json_data', core.models.EncryptedTextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('key', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='auth_token', to='api.APIUser')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]