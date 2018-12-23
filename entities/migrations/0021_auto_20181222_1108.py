# Generated by Django 2.1.4 on 2018-12-22 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0020_syncmodel_last_sync_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ismrelinvm',
            name='change_id',
            field=models.BigIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='ismrelinvm',
            name='f_rel_inv_idn',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='ismrelinvm',
            name='row_id',
            field=models.CharField(db_index=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='ismrelletd',
            name='change_id',
            field=models.BigIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='ismrelletd',
            name='f_rel_let_idn',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='ismrelletd',
            name='row_id',
            field=models.CharField(db_index=True, max_length=50),
        ),
    ]
