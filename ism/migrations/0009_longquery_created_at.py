# Generated by Django 2.1.4 on 2018-12-31 02:56

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ism', '0008_auto_20181226_0959'),
    ]

    operations = [
        migrations.AddField(
            model_name='longquery',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
