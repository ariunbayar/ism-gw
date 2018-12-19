# Generated by Django 2.1.4 on 2018-12-17 16:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SyncModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='SyncModelColumns',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('ism_name', models.CharField(max_length=255)),
                ('enabled', models.BooleanField()),
                ('modelsync', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='entities.SyncModel')),
            ],
        ),
    ]