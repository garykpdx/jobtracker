# Generated by Django 5.0.6 on 2024-06-16 20:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobapps', '0003_alter_jobapp_applied_dt_alter_jobapp_city_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobapp',
            name='slug',
        ),
    ]
