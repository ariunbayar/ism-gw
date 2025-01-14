# Generated by Django 2.1.4 on 2018-12-24 02:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FetchItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=255)),
                ('ism_name', models.CharField(max_length=255)),
                ('data', models.BinaryField(null=True)),
                ('prev_change_id', models.BigIntegerField(null=True)),
                ('last_change_id', models.BigIntegerField(null=True)),
                ('last_sync_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
