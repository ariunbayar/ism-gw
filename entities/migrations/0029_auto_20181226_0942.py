# Generated by Django 2.1.4 on 2018-12-26 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0028_ismtoadplantable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ismpspalnm',
            name='f_bir_day',
            field=models.CharField(db_index=True, max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name='ismpspalnm',
            name='f_gen_cde',
            field=models.CharField(db_index=True, max_length=3, null=True),
        ),
    ]