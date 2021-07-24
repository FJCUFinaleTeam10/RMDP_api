# Generated by Django 3.2.5 on 2021-07-23 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('longitude', models.CharField(max_length=100)),
                ('latitude', models.CharField(max_length=100)),
                ('velocity', models.FloatField()),
                ('capacity', models.FloatField()),
            ],
            options={
                'db_table': 'driver',
            },
        ),
    ]
