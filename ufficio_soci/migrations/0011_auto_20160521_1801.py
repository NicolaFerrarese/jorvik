# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-21 18:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ufficio_soci', '0010_issue_194_pregresso'),
    ]

    operations = [
        migrations.AddField(
            model_name='tesseramento',
            name='fine_soci',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='tesseramento',
            name='fine_soci_iv',
            field=models.DateField(null=True),
        ),
    ]
