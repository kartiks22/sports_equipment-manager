# Generated by Django 2.2.12 on 2020-05-18 12:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sportsEquipment', '0006_auto_20200518_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipments',
            name='eqpQuantityTaken',
            field=models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(0)]),
        ),
    ]
