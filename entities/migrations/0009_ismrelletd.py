# Generated by Django 2.1.4 on 2018-12-18 00:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0008_syncmodel_ism_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='IsmRelLetD',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('f_rel_inq_idn', models.IntegerField(null=True)),
                ('f_rel_let_idn', models.IntegerField()),
                ('f_del_cde', models.CharField(max_length=3, null=True)),
                ('f_edt_day', models.CharField(max_length=8, null=True)),
                ('f_edt_dtm', models.DateTimeField(null=True)),
                ('f_edt_ocp_cde', models.CharField(max_length=5, null=True)),
                ('f_edt_prt_cde', models.CharField(max_length=4, null=True)),
                ('f_inv_vio_srn', models.IntegerField(null=True)),
                ('f_iss_dpt_cde', models.CharField(max_length=3, null=True)),
                ('f_iss_opr_day', models.CharField(max_length=8, null=True)),
                ('f_iss_opr_num', models.CharField(max_length=20, null=True)),
                ('f_ivd_cde', models.CharField(max_length=3, null=True)),
                ('f_ivd_day', models.CharField(max_length=8, null=True)),
                ('f_ivd_ocp_cde', models.CharField(max_length=5, null=True)),
                ('f_ivd_opr_day', models.CharField(max_length=8, null=True)),
                ('f_ivd_opr_num', models.CharField(max_length=20, null=True)),
                ('f_ivd_prt_cde', models.CharField(max_length=4, null=True)),
                ('f_ivd_rsn_cde', models.CharField(max_length=3, null=True)),
                ('f_let_cde', models.CharField(max_length=3, null=True)),
                ('f_lev_prd_day', models.CharField(max_length=8, null=True)),
                ('f_pnh_tag_cde', models.CharField(max_length=3, null=True)),
                ('f_reg_day', models.CharField(max_length=8, null=True)),
                ('f_reg_ocp_cde', models.CharField(max_length=5, null=True)),
                ('f_reg_prt_cde', models.CharField(max_length=4, null=True)),
                ('f_rel_inv_idn', models.IntegerField(null=True)),
                ('f_vrf_ocp_cde', models.CharField(max_length=5, null=True)),
            ],
            options={
                'db_table': 'ISM_T_REL_LET_D',
            },
        ),
    ]