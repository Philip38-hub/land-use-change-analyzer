# Generated by Django 5.2 on 2025-04-16 19:02

import analyzer.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='LandUseClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='AerialImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=analyzer.models.get_upload_path)),
                ('year', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('classified_image', models.ImageField(blank=True, null=True, upload_to='results')),
                ('extent_north', models.FloatField(blank=True, null=True)),
                ('extent_south', models.FloatField(blank=True, null=True)),
                ('extent_east', models.FloatField(blank=True, null=True)),
                ('extent_west', models.FloatField(blank=True, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='analyzer.analysisproject')),
            ],
        ),
        migrations.CreateModel(
            name='AnalysisResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change_map', models.ImageField(blank=True, null=True, upload_to='results')),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
                ('earlier_image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='earlier_results', to='analyzer.aerialimage')),
                ('later_image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='later_results', to='analyzer.aerialimage')),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='analyzer.analysisproject')),
            ],
        ),
        migrations.CreateModel(
            name='ChangeStatistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area_pixels', models.IntegerField()),
                ('percentage', models.FloatField()),
                ('result', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='change_statistics', to='analyzer.analysisresult')),
                ('from_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='changes_from', to='analyzer.landuseclass')),
                ('to_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='changes_to', to='analyzer.landuseclass')),
            ],
        ),
        migrations.CreateModel(
            name='LandUseStatistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area_pixels', models.IntegerField()),
                ('percentage', models.FloatField()),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statistics', to='analyzer.aerialimage')),
                ('land_use_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analyzer.landuseclass')),
            ],
        ),
    ]
