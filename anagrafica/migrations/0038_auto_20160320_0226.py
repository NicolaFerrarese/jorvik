# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-20 02:26
from __future__ import unicode_literals

import base.utils
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0037_auto_20160311_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='persona',
            name='cognome',
            field=base.utils.TitleCharField(db_index=True, max_length=64, verbose_name='Cognome'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='comune_nascita',
            field=base.utils.TitleCharField(blank=True, max_length=64, verbose_name='Comune di Nascita'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='comune_residenza',
            field=base.utils.TitleCharField(max_length=64, null=True, verbose_name='Comune di residenza'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='indirizzo_residenza',
            field=base.utils.TitleCharField(max_length=512, null=True, verbose_name='Indirizzo di residenza'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='nome',
            field=base.utils.TitleCharField(db_index=True, max_length=64, verbose_name='Nome'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='provincia_nascita',
            field=base.utils.TitleCharField(blank=True, max_length=2, verbose_name='Provincia di Nascita'),
        ),
        migrations.AlterField(
            model_name='persona',
            name='provincia_residenza',
            field=base.utils.TitleCharField(max_length=2, null=True, verbose_name='Provincia di residenza'),
        ),
    ]