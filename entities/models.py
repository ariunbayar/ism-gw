from django.db import models
from django.apps import apps


class SyncModel(models.Model):
    model_name = models.CharField(max_length=255)
    ism_name = models.CharField(max_length=255)
    is_enabled = models.BooleanField()

    def get_model(self):
        return apps.get_model('entities', self.model_name)


class SyncModelColumn(models.Model):
    syncmodel = models.ForeignKey(SyncModel, on_delete=models.PROTECT, related_name='columns')
    name = models.CharField(max_length=255)
    ism_name = models.CharField(max_length=255)
    is_enabled = models.BooleanField()
    is_pk = models.BooleanField()


class SyncStatus(models.Model):

    # fetch_status = models.ForeignKey('self', on_delete=models.PROTECT, related_name='columns')
    sync_model = models.ForeignKey(SyncModel, on_delete=models.PROTECT, null=True)
    duration_ms = models.IntegerField()
    stopped_at = models.DateTimeField(auto_now_add=True)


class GracefulErrors(models.Model):

    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


class IsmRelInvVioD(models.Model):

    class Meta:
        db_table = 'ISM_T_REL_INV_VIO_D'

    change_id = models.BigIntegerField()
    row_id = models.CharField(max_length=50)

    f_rel_inq_idn = models.IntegerField()
    f_rel_inv_idn = models.IntegerField()
    f_inv_vio_srn = models.IntegerField()
    f_del_cde = models.CharField(null=True, max_length=3)
    f_edt_day = models.CharField(null=True, max_length=8)
    f_edt_dtm = models.DateTimeField(null=True)
    f_edt_ocp_cde = models.CharField(null=True, max_length=5)
    f_edt_prt_cde = models.CharField(null=True, max_length=4)
    f_exp_day = models.CharField(null=True, max_length=8)
    f_inv_acm_cde = models.CharField(null=True, max_length=5)
    f_inv_dtl = models.CharField(null=True, max_length=1000)
    f_ivd_cde = models.CharField(null=True, max_length=3)
    f_ivd_day = models.CharField(null=True, max_length=8)
    f_ivd_ocp_cde = models.CharField(null=True, max_length=5)
    f_ivd_opr_day = models.CharField(null=True, max_length=8)
    f_ivd_opr_num = models.CharField(null=True, max_length=20)
    f_ivd_prt_cde = models.CharField(null=True, max_length=4)
    f_ivd_rsn_cde = models.CharField(null=True, max_length=3)
    f_law_cde = models.CharField(null=True, max_length=3)
    f_law_knd_cde = models.CharField(null=True, max_length=3)
    f_law_vio_dtl = models.CharField(null=True, max_length=1000)
    f_reg_day = models.CharField(null=True, max_length=8)
    f_reg_ocp_cde = models.CharField(null=True, max_length=5)
    f_reg_prt_cde = models.CharField(null=True, max_length=4)
    f_vio_ctn = models.CharField(null=True, max_length=1000)
    f_vio_day = models.CharField(null=True, max_length=8)
    f_vio_dtl = models.CharField(null=True, max_length=1000)
    f_vio_opn = models.CharField(null=True, max_length=1000)
    f_vio_opr_day = models.CharField(null=True, max_length=8)
    f_vio_opr_num = models.CharField(null=True, max_length=50)
    f_vio_pla = models.CharField(null=True, max_length=200)
    f_vio_rsn_cde = models.CharField(null=True, max_length=3)


class IsmRelLetD(models.Model):

    class Meta:
        db_table = 'ISM_T_REL_LET_D'

    change_id = models.BigIntegerField()
    row_id = models.CharField(max_length=50)

    f_rel_inq_idn = models.IntegerField(null=True)
    f_rel_let_idn = models.IntegerField()
    f_del_cde = models.CharField(null=True, max_length=3)
    f_edt_day = models.CharField(null=True, max_length=8)
    f_edt_dtm = models.DateTimeField(null=True)
    f_edt_ocp_cde = models.CharField(null=True, max_length=5)
    f_edt_prt_cde = models.CharField(null=True, max_length=4)
    f_inv_vio_srn = models.IntegerField(null=True)
    f_iss_dpt_cde = models.CharField(null=True, max_length=3)
    f_iss_opr_day = models.CharField(null=True, max_length=8)
    f_iss_opr_num = models.CharField(null=True, max_length=20)
    f_ivd_cde = models.CharField(null=True, max_length=3)
    f_ivd_day = models.CharField(null=True, max_length=8)
    f_ivd_ocp_cde = models.CharField(null=True, max_length=5)
    f_ivd_opr_day = models.CharField(null=True, max_length=8)
    f_ivd_opr_num = models.CharField(null=True, max_length=20)
    f_ivd_prt_cde = models.CharField(null=True, max_length=4)
    f_ivd_rsn_cde = models.CharField(null=True, max_length=3)
    f_let_cde = models.CharField(null=True, max_length=3)
    f_lev_prd_day = models.CharField(null=True, max_length=8)
    f_pnh_tag_cde = models.CharField(null=True, max_length=3)
    f_reg_day = models.CharField(null=True, max_length=8)
    f_reg_ocp_cde = models.CharField(null=True, max_length=5)
    f_reg_prt_cde = models.CharField(null=True, max_length=4)
    f_rel_inv_idn = models.IntegerField(null=True)
    f_vrf_ocp_cde = models.CharField(null=True, max_length=5)


class IsmRelInvM(models.Model):

    class Meta:
        db_table = 'ISM_T_REL_INV_M'

    change_id = models.BigIntegerField()
    row_id = models.CharField(max_length=50)

    f_aln_idn = models.IntegerField(null=True)
    f_aln_psp_idn = models.IntegerField(null=True)
    f_dom_idn = models.IntegerField(null=True)
    f_dom_psp_idn = models.IntegerField(null=True)
    f_rel_inq_idn = models.IntegerField(null=True)
    f_sty_idn = models.IntegerField(null=True)
    f_vsa_idn = models.IntegerField(null=True)
    f_rel_inv_idn = models.IntegerField()
    f_dcs_day = models.CharField(null=True, max_length=8)
    f_dcs_ocp_cde = models.CharField(null=True, max_length=5)
    f_dcs_prs_cde = models.CharField(null=True, max_length=3)
    f_del_cde = models.CharField(null=True, max_length=3)
    f_doa_cde = models.CharField(null=True, max_length=3)
    f_edt_day = models.CharField(null=True, max_length=8)
    f_edt_dtm = models.DateTimeField(null=True)
    f_edt_ocp_cde = models.CharField(null=True, max_length=5)
    f_edt_prt_cde = models.CharField(null=True, max_length=4)
    f_inv_ara_cde = models.CharField(null=True, max_length=4)
    f_inv_cti = models.CharField(null=True, max_length=50)
    f_inv_cty_cde = models.CharField(null=True, max_length=3)
    f_inv_day = models.CharField(null=True, max_length=8)
    f_inv_dtl = models.CharField(null=True, max_length=200)
    f_inv_kur = models.CharField(null=True, max_length=100)
    f_inv_ocp_cde = models.CharField(null=True, max_length=5)
    f_inv_prs_cde = models.CharField(null=True, max_length=3)
    f_inv_vrf_cde = models.CharField(null=True, max_length=5)
    f_ivd_cde = models.CharField(null=True, max_length=3)
    f_ivd_day = models.CharField(null=True, max_length=8)
    f_ivd_ocp_cde = models.CharField(null=True, max_length=5)
    f_ivd_opr_day = models.CharField(null=True, max_length=8)
    f_ivd_opr_num = models.CharField(null=True, max_length=20)
    f_ivd_prt_cde = models.CharField(null=True, max_length=4)
    f_ivd_rsn_cde = models.CharField(null=True, max_length=3)
    f_mak_day = models.CharField(null=True, max_length=8)
    f_mak_ocp_cde = models.CharField(null=True, max_length=5)
    f_mak_prs_cde = models.CharField(null=True, max_length=3)
    f_reg_day = models.CharField(null=True, max_length=8)
    f_reg_ocp_cde = models.CharField(null=True, max_length=5)
    f_reg_pla = models.CharField(null=True, max_length=200)
    f_reg_prt_cde = models.CharField(null=True, max_length=4)
