# Generated by Django 2.1.1 on 2020-03-13 13:05

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_auto_20200313_1305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wikiarticle',
            name='date',
            field=models.DateField(default=datetime.datetime(2020, 3, 13, 13, 5, 41, 236934, tzinfo=utc)),
        ),
    ]
