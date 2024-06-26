# Generated by Django 5.0.6 on 2024-06-21 23:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobapps', '0004_remove_jobapp_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobapp',
            name='job_status',
            field=models.CharField(choices=[('APPLIED', 'Applied'), ('QUALIFIED', 'Qualified'), ('INTERVIEWED', 'Interviewed'), ('CLOSED', 'Closed'), ('OFFERED', 'Offered Job')], default='APPLIED', max_length=15),
        ),
        migrations.AlterField(
            model_name='jobapp',
            name='location_type',
            field=models.CharField(choices=[('ONSITE', 'Onsite'), ('HYBRID', 'Hybrid'), ('REMOTE', 'Remote')], max_length=10),
        ),
    ]
