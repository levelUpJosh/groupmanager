# Generated by Django 2.2.7 on 2020-01-29 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groupsapp', '0010_usergrouplink'),
    ]

    operations = [
        migrations.AlterField(
            model_name='member',
            name='dob',
            field=models.DateField(verbose_name='Date of Birth'),
        ),
    ]
