# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-26 06:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20170626_0217'),
    ]

    operations = [
        migrations.RenameField(
            model_name='alertapolicial',
            old_name='idAlumno',
            new_name='idUsuario',
        ),
    ]