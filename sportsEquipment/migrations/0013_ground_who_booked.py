# Generated by Django 2.1.5 on 2020-05-23 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sportsEquipment', '0012_ground_booked'),
    ]

    operations = [
        migrations.AddField(
            model_name='ground',
            name='who_booked',
            field=models.TextField(default=';'),
        ),
    ]
