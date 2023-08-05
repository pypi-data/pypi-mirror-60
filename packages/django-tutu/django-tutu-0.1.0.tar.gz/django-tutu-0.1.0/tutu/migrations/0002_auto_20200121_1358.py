# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-01-21 20:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tutu', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alert_on', models.BooleanField()),
                ('did_action', models.BooleanField(default=False)),
                ('alert_name', models.TextField()),
                ('actions_performed', models.TextField()),
                ('tick', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tutu.Tick')),
            ],
            options={
                'get_latest_by': 'tick__date',
            },
        ),
        migrations.AlterModelOptions(
            name='pollresult',
            options={'get_latest_by': 'tick__date'},
        ),
    ]
