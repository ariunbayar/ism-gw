# Generated by Django 2.1.4 on 2018-12-24 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ism', '0004_fetchitem_num_rows'),
    ]

    operations = [
        migrations.CreateModel(
            name='LongQuery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query', models.TextField()),
                ('args', models.TextField()),
                ('duration_ms', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='fetchitem',
            name='duration_ms',
            field=models.IntegerField(default=0),
        ),
    ]