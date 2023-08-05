# Generated by Django 2.1.11 on 2019-09-23 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djautotask', '0009_auto_20190918_1525'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='completed_date_time',
        ),
        migrations.RemoveField(
            model_name='project',
            name='end_date_time',
        ),
        migrations.RemoveField(
            model_name='project',
            name='start_date_time',
        ),
        migrations.AddField(
            model_name='project',
            name='completed_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='end_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='start_date',
            field=models.DateField(null=True),
        ),
    ]
