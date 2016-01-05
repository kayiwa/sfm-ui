# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ui', '0003_auto_20151202_2215'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='note',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='seed',
            name='note',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='seedset',
            name='note',
            field=models.TextField(blank=True),
        ),
    ]
