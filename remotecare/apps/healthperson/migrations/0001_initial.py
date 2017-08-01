# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-23 21:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='HealthPerson',
            fields=[
                ('id',
                 models.AutoField(auto_created=True,
                                  primary_key=True,
                                  serialize=False,
                                  verbose_name='ID')),
                ('added_on', models.DateField(auto_now_add=True)),
                ('added_by',
                 models.ForeignKey(blank=True,
                                   null=True,
                                   on_delete=django.db.models.deletion.CASCADE,
                                   to='healthperson.HealthPerson')),
                ('polymorphic_ctype',
                 models.ForeignKey(editable=False,
                                   null=True,
                                   on_delete=django.db.models.deletion.CASCADE,
                                   related_name='polymorphic_healthperson.healthperson_set+',
                                   to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
