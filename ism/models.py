from django.db import models
from entities.models import SyncModel
from entities.models import IsmPspAlnM


class FetchItem(models.Model):

    syncmodel = models.ForeignKey(SyncModel, on_delete=models.PROTECT)

    begin_row_id = models.CharField(max_length=50, db_index=True, null=True)
    begin_change_id = models.BigIntegerField(null=True, db_index=True)

    last_row_id = models.CharField(max_length=50, db_index=True, null=True)
    last_change_id = models.BigIntegerField(null=True, db_index=True)

    num_rows = models.IntegerField(default=0)
    data = models.BinaryField(null=True)
    duration_ms = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)


class LongQuery(models.Model):

    query = models.TextField()
    args = models.TextField()
    duration_ms = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
