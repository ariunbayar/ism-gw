# Generated by Django 2.1.4 on 2018-12-24 02:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('entities', '0028_ismtoadplantable'),
        ('ism', '0002_delete_fetchitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='FetchItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.BinaryField(null=True)),
                ('begin_row_id', models.CharField(db_index=True, max_length=50, null=True)),
                ('begin_change_id', models.BigIntegerField(db_index=True, null=True)),
                ('last_row_id', models.CharField(db_index=True, max_length=50, null=True)),
                ('last_change_id', models.BigIntegerField(db_index=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('syncmodel', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='entities.SyncModel')),
            ],
        ),
    ]