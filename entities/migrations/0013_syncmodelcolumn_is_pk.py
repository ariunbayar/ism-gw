# Generated by Django 2.1.4 on 2018-12-19 08:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0012_auto_20181219_1256'),
    ]

    operations = [
        migrations.AddField(
            model_name='syncmodelcolumn',
            name='is_pk',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
