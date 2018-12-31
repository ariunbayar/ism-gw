import json
import time
from datetime import datetime

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection, models, transaction
from django.utils import timezone

from main.utils import connect_db
from entities.models import SyncModel
from entities.models import SyncStatus
from entities.models import SyncStatus
from ism.models import LongQuery


NUM_ITEMS_PER_MODEL = 100000


class Command(BaseCommand):

    def exec_query(self, *args, **kwargs):
        started_at = time.time()
        result = self._exec_query(*args, **kwargs)
        duration_ms = int((time.time() - started_at) * 1000)
        if duration_ms > 1000:
            q = LongQuery()
            q.query = args[0].strip()
            q.args = json.dumps(kwargs)
            q.duration_ms = duration_ms
            q.save()

        return result

    def handle(self, *args, **options):

        global_started_at = time.time()

        sync_models = SyncModel.objects.filter(is_enabled=True)

        global_sync_status = SyncStatus()
        global_sync_status.sync_model = None

        with connect_db() as exec_query:
            self._exec_query = exec_query

            for sync_model in sync_models:

                print("=== Model: %s (%s)" % (sync_model.model_name, sync_model.ism_name))
                last_change_id = sync_model.last_change_id
                last_row_id = sync_model.last_row_id

                has_more = True

                while has_more:
                    with transaction.atomic():
                        started_at = time.time()
                        columns = sync_model.columns.filter(is_enabled=True)

                        # Fetching
                        row_iter = self.fetch_greater_than_last(sync_model, columns, NUM_ITEMS_PER_MODEL, last_change_id, last_row_id)

                        # Storing
                        sync_status = SyncStatus()
                        sync_status.sync_model = sync_model

                        sync_status.num_fetched = 0
                        sync_status.num_duplicates = 0
                        sync_status.num_created = 0
                        sync_status.num_updated = 0
                        Model = sync_model.get_model()
                        for row in row_iter:
                            is_duplicate, is_created, is_updated = self.save(Model, row, columns)
                            if sync_status.num_fetched % 100 == 0:
                                print('.', end='')
                            sync_status.num_fetched    += 1
                            sync_status.num_duplicates += 1 if is_duplicate else 0
                            sync_status.num_created    += 1 if is_created else 0
                            sync_status.num_updated    += 1 if is_updated else 0
                            last_change_id = row.ORA_ROWSCN
                            last_row_id = row.ROWID

                        if sync_status.num_fetched > 0:
                            print('Fetched: %s' % sync_status.num_fetched)

                            sync_model.last_change_id = last_change_id
                            sync_model.last_row_id = last_row_id
                            sync_model.save()

                            global_sync_status.num_fetched    += sync_status.num_fetched
                            global_sync_status.num_duplicates += sync_status.num_duplicates
                            global_sync_status.num_created    += sync_status.num_created
                            global_sync_status.num_updated    += sync_status.num_updated

                            sync_status.duration_ms = int(1000 * (time.time() - started_at))
                            sync_status.save()
                        has_more = sync_status.num_fetched >= NUM_ITEMS_PER_MODEL

                sync_model.last_sync_at = timezone.now()
                sync_model.save()

        global_sync_status.duration_ms = int(1000 * (time.time() - global_started_at))
        global_sync_status.save()

    def save(self, Model, row, columns):

        is_duplicate = False
        is_created = False
        is_updated = False

        # Duplication by tracking values are ignored
        instance = Model.objects.filter(change_id=row.ORA_ROWSCN, row_id=row.ROWID).first()
        is_duplicate = instance is not None
        if instance:
            return is_duplicate, is_created, is_updated

        pk_values = dict([(col.name, getattr(row, col.ism_name)) for col in columns if col.is_pk])
        if len(pk_values):
            try:
                instance = Model.objects.get(**pk_values)
                is_updated = True
            except Model.DoesNotExist:
                is_created = True
                instance = Model()
        else:
            is_created = True
            instance = Model()

        instance.change_id = row.ORA_ROWSCN
        instance.row_id = row.ROWID
        for col in columns:
            setattr(instance, col.name, getattr(row, col.ism_name))
        instance.save()

        return is_duplicate, is_created, is_updated


    def fetch_greater_than_last(self, sync_model, columns, num_rows, last_change_id=None, last_row_id=None):
        query = """
                SELECT * FROM (
                    SELECT
                        ORA_ROWSCN, ROWID, {fields}
                    FROM
                        ISM.{table}
                    {additional_condition}
                    ORDER BY
                        ORA_ROWSCN ASC, ROWID ASC
                ) WHERE ROWNUM <= :prownummax
            """

        fields = []
        for col in columns:
            if col.aggregation and '{0}' in col.aggregation:
                fields.append(col.aggregation.format(col.ism_name) + ' as ' + col.ism_name)
            else:
                fields.append(col.ism_name)

        format_args = {
                'fields': ', '.join(fields),
                'table': sync_model.ism_name,
                'additional_condition': '',
            }

        params = {
                'prownummax': num_rows,
            }

        if last_change_id and last_row_id:
            format_args['additional_condition'] = 'WHERE ((ORA_ROWSCN > :prowscn) OR (ORA_ROWSCN = :prowscn AND ROWID > :prowid))'
            params['prowscn'] = last_change_id
            params['prowid'] = last_row_id

        elif last_change_id and last_row_id is None:
            format_args['additional_condition'] = 'WHERE ORA_ROWSCN > :prowscn'
            params['prowscn'] = last_change_id

        sql = query.format(**format_args)

        return self.exec_query(sql, **params)
