# Generated by Django 2.1.4 on 2018-12-18 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0007_auto_20181218_0721'),
    ]

    operations = [
        migrations.AddField(
            model_name='syncmodel',
            name='ism_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
