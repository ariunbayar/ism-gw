from django.db import models
from django.apps import apps


class SyncModel(models.Model):
    model_name = models.CharField(max_length=255)
    ism_name = models.CharField(max_length=255)
    is_enabled = models.BooleanField()
    last_change_id = models.BigIntegerField(null=True)
    last_sync_at = models.DateTimeField(null=True)

    def get_model(self):
        return apps.get_model('entities', self.model_name)


class SyncModelColumn(models.Model):
    syncmodel = models.ForeignKey(SyncModel, on_delete=models.PROTECT, related_name='columns')
    name = models.CharField(max_length=255)
    ism_name = models.CharField(max_length=255)
    aggregation = models.CharField(max_length=255, null=True)
    is_enabled = models.BooleanField()
    is_pk = models.BooleanField()


class SyncStatus(models.Model):

    # fetch_status = models.ForeignKey('self', on_delete=models.PROTECT, related_name='columns')
    sync_model = models.ForeignKey(SyncModel, on_delete=models.PROTECT, null=True)
    duration_ms = models.IntegerField()
    stopped_at = models.DateTimeField(auto_now_add=True)

    num_fetch_expected  = models.IntegerField(default=0)
    num_fetched         = models.IntegerField(default=0)
    num_duplicates      = models.IntegerField(default=0)
    num_created         = models.IntegerField(default=0)
    num_updated         = models.IntegerField(default=0)


class GracefulErrors(models.Model):

    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


class IsmRelInvVioD(models.Model):

    class Meta:
        db_table = 'ISM_T_REL_INV_VIO_D'

    change_id = models.BigIntegerField(db_index=True)
    row_id = models.CharField(max_length=50, db_index=True)

    f_rel_inq_idn = models.IntegerField(db_index=True)
    f_rel_inv_idn = models.IntegerField(db_index=True)
    f_inv_vio_srn = models.IntegerField(db_index=True)
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

    change_id = models.BigIntegerField(db_index=True)
    row_id = models.CharField(max_length=50, db_index=True)

    f_rel_inq_idn = models.IntegerField(null=True)
    f_rel_let_idn = models.IntegerField(db_index=True)
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

    change_id = models.BigIntegerField(db_index=True)
    row_id = models.CharField(max_length=50, db_index=True)

    f_aln_idn = models.IntegerField(null=True)
    f_aln_psp_idn = models.IntegerField(null=True)
    f_dom_idn = models.IntegerField(null=True)
    f_dom_psp_idn = models.IntegerField(null=True)
    f_rel_inq_idn = models.IntegerField(null=True)
    f_sty_idn = models.IntegerField(null=True)
    f_vsa_idn = models.IntegerField(null=True)
    f_rel_inv_idn = models.IntegerField(db_index=True)
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


class IsmPspAlnM(models.Model):

    class Meta:
        db_table = 'ISM_T_PSP_ALN_M'

    change_id = models.IntegerField(db_index=True)
    row_id = models.CharField(max_length=50, db_index=True)

    f_aln_idn = models.IntegerField(null=True)
    f_aln_psp_idn = models.IntegerField(db_index=True)
    f_bir_day = models.CharField(null=True, max_length=8)
    f_fnm_gnr = models.CharField(null=True, max_length=50)
    f_fnm_nam = models.CharField(null=True, max_length=50)
    f_gen_cde = models.CharField(null=True, max_length=3)
    f_ntl_cde = models.CharField(null=True, max_length=3)
    f_psp_num = models.CharField(null=True, max_length=40)
    f_abb_nam = models.CharField(null=True, max_length=10)
    f_all_nam = models.CharField(null=True, max_length=100)
    f_ccl_yon_cde = models.CharField(null=True, max_length=3)
    f_crw_idn = models.IntegerField(null=True)
    f_dbl_reg_rsn = models.CharField(null=True, max_length=10)
    f_del_cde = models.CharField(null=True, max_length=3)
    f_edt_day = models.CharField(null=True, max_length=8)
    f_edt_dtm = models.DateTimeField(null=True)
    f_edt_ocp_cde = models.CharField(null=True, max_length=5)
    f_edt_prt_cde = models.CharField(null=True, max_length=4)
    f_epr_day = models.CharField(null=True, max_length=8)
    f_etr_uyn_cde = models.CharField(null=True, max_length=3)
    f_fnm_trb = models.CharField(null=True, max_length=50)
    f_isc_iss_cpn = models.CharField(null=True, max_length=100)
    f_isc_ntl_cde = models.CharField(null=True, max_length=3)
    f_isc_rsd_num = models.CharField(null=True, max_length=20)
    f_iss_day = models.CharField(null=True, max_length=8)
    f_ivd_cde = models.CharField(null=True, max_length=3)
    f_ivd_day = models.CharField(null=True, max_length=8)
    f_ivd_ocp_cde = models.CharField(null=True, max_length=5)
    f_ivd_prt_cde = models.CharField(null=True, max_length=4)
    f_lev_uyn_cde = models.CharField(null=True, max_length=3)
    f_psp_clf_cde = models.CharField(null=True, max_length=3)
    f_psp_knd_cde = models.CharField(null=True, max_length=3)
    f_psp_pic = models.BinaryField(null=True)
    f_psp_typ_cde = models.CharField(null=True, max_length=3)
    f_psp_use_cut = models.IntegerField(null=True)
    f_reg_day = models.CharField(null=True, max_length=8)
    f_reg_ocp_cde = models.CharField(null=True, max_length=5)
    f_reg_prt_cde = models.CharField(null=True, max_length=4)
    f_rsd_num_eng = models.CharField(null=True, max_length=16)
    f_rsd_num_mga = models.CharField(null=True, max_length=16)
    f_sgl_yon_cde = models.CharField(null=True, max_length=3)
