# Generated by Django 2.2.7 on 2019-11-30 18:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groupsapp', '0002_auto_20191130_1222'),
    ]

    operations = [
        migrations.CreateModel(
            name='JoinCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=8)),
                ('role', models.CharField(max_length=20)),
                ('maxNo', models.IntegerField(default=1)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groupsapp.Group')),
            ],
        ),
    ]
