# Generated by Django 2.1.4 on 2018-12-26 01:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ism', '0007_auto_20181226_0942'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SearchDoc',
        ),
        migrations.DeleteModel(
            name='SearchIndex',
        ),
    ]