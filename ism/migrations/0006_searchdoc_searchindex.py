# Generated by Django 2.1.4 on 2018-12-25 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ism', '0005_auto_20181224_1157'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchDoc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('searchindex_id', models.IntegerField()),
                ('doc_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SearchIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(db_index=True, max_length=250)),
                ('count', models.IntegerField(default=0)),
            ],
        ),
    ]
