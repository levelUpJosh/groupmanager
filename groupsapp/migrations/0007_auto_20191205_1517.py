# Generated by Django 2.2.7 on 2019-12-05 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupsapp', '0006_auto_20191201_1538'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='group_name',
            field=models.CharField(max_length=15),
        ),
    ]
