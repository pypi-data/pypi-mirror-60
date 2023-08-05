# Generated by Django 3.0.2 on 2020-01-03 13:37

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('is_active', models.BooleanField(default=False)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('iso_alpha_3', models.CharField(max_length=3, unique=True, validators=[django.core.validators.MinLengthValidator(3)])),
                ('iso_alpha_2', models.CharField(max_length=2, unique=True, validators=[django.core.validators.MinLengthValidator(2)])),
                ('iso_num', models.IntegerField(unique=True)),
                ('flag', models.ImageField(blank=True, null=True, upload_to='pixelforest_drf/flags/')),
            ],
            options={
                'verbose_name_plural': 'Countries',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('is_active', models.BooleanField(default=False)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('abbreviation', models.CharField(blank=True, max_length=5, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubRegion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('is_active', models.BooleanField(default=False)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('abbreviation', models.CharField(blank=True, max_length=5, null=True)),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='countries.Region')),
            ],
        ),
        migrations.AddConstraint(
            model_name='region',
            constraint=models.UniqueConstraint(fields=('name',), name='Two regions cannot share the same name'),
        ),
        migrations.AddConstraint(
            model_name='region',
            constraint=models.UniqueConstraint(fields=('abbreviation',), name='Two regions cannot share the same abbreviation'),
        ),
        migrations.AddField(
            model_name='country',
            name='sub_region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='countries.SubRegion'),
        ),
        migrations.AddConstraint(
            model_name='subregion',
            constraint=models.UniqueConstraint(fields=('region', 'name'), name='Two sub regions cannot share the same name and region.'),
        ),
        migrations.AddConstraint(
            model_name='subregion',
            constraint=models.UniqueConstraint(fields=('region', 'abbreviation'), name='Two sub regions cannot share the same abbreviation and region.'),
        ),
        migrations.AddConstraint(
            model_name='country',
            constraint=models.UniqueConstraint(fields=('sub_region', 'name'), name='Two countries cannot share the same name and sub_region'),
        ),
    ]
