# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-23 21:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('id',
                 models.AutoField(auto_created=True,
                                  primary_key=True,
                                  serialize=False,
                                  verbose_name='ID')),
                ('abbreviation', models.CharField(max_length=20)),
                ('full_name', models.CharField(max_length=255)),
                ('city',
                 models.CharField(blank=True,
                                  max_length=128,
                                  null=True)),
                ('created', models.DateTimeField()),
                ('modified', models.DateTimeField()),
                ('tags', models.TextField()),
            ],
            options={
                'ordering': ('abbreviation',),
            },
        ),
    ]
