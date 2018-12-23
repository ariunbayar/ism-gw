import time
from datetime import datetime

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection, models, transaction
from django.utils import timezone

from main.utils import connect_db
from entities.models import SyncModel
from entities.models import SyncStatus


# NUM_ITEMS_PER_MODEL = 3
NUM_ITEMS_PER_MODEL = 2000


class Command(BaseCommand):

    def exec_query(self, *args, **kwargs):
        started_at = time.time()
        result = self._exec_query(*args, **kwargs)
        duration_ms = int((time.time() - started_at) * 1000)
        if duration_ms > 5000:
            print('Long query: %sms' % (duration_ms))
            print(args[0].strip())
            import pprint; pprint.pprint(kwargs)

        return result

    def handle(self, *args, **options):

        global_started_at = time.time()

        sync_models = SyncModel.objects.filter(is_enabled=True)

        global_sync_status = SyncStatus()
        global_sync_status.sync_model = None

        with connect_db() as exec_query:
            self._exec_query = exec_query

            for sync_model in sync_models:
                last_change_id = sync_model.last_change_id

                has_more = True

                while has_more:
                    with transaction.atomic():
                        started_at = time.time()
                        fetch_status = self.fetch_since(sync_model, NUM_ITEMS_PER_MODEL, last_change_id)
                        if fetch_status['num_fetch_expected'] > 0:
                            has_more = fetch_status['num_fetch_expected'] >= NUM_ITEMS_PER_MODEL

                            last_change_id = fetch_status['last_change_id']
                            print('Fetched: %s' % fetch_status['num_fetch_expected'])

                            sync_model.last_change_id = fetch_status['last_change_id']
                            sync_model.last_sync_at = timezone.now()
                            sync_model.save()

                            sync_status = SyncStatus()
                            sync_status.sync_model = sync_model
                            sync_status.duration_ms = int(1000 * (time.time() - started_at))
                            sync_status.num_fetch_expected  = fetch_status['num_fetch_expected']
                            sync_status.num_fetched         = fetch_status['num_fetched']
                            sync_status.num_duplicates      = fetch_status['num_duplicates']
                            sync_status.num_created         = fetch_status['num_created']
                            sync_status.num_updated         = fetch_status['num_updated']
                            sync_status.save()
                        else:
                            has_more = False

                global_sync_status.num_fetch_expected  += fetch_status['num_fetch_expected']
                global_sync_status.num_fetched         += fetch_status['num_fetched']
                global_sync_status.num_duplicates      += fetch_status['num_duplicates']
                global_sync_status.num_created         += fetch_status['num_created']
                global_sync_status.num_updated         += fetch_status['num_updated']

        global_sync_status.duration_ms = int(1000 * (time.time() - global_started_at))
        global_sync_status.save()

    def fetch_since(self, sync_model, num_rows, last_change_id):

        Model = sync_model.get_model()

        change_ids = self.get_change_ids(sync_model, num_rows, last_change_id)
        columns = sync_model.columns.filter(is_enabled=True)

        num_fetch_expected = self.count_by_change_ids(sync_model, change_ids)
        num_fetched = 0
        num_duplicates = 0
        num_created = 0
        num_updated = 0

        last_row_id = None

        while num_fetched < num_fetch_expected:
            rows = self.fetch_greater_than_last(sync_model, columns, change_ids, num_rows, last_change_id, last_row_id)

            for row in rows:
                is_duplicate, is_created, is_updated = self.save(Model, row, columns)
                num_fetched += 1
                num_created += 1 if is_created else 0
                num_updated += 1 if is_updated else 0
                num_duplicates += 1 if is_duplicate else 0
                last_change_id = row.ORA_ROWSCN
                last_row_id = row.ROWID

        return {
                'num_fetch_expected': num_fetch_expected,
                'num_fetched': num_fetched,
                'num_duplicates': num_duplicates,
                'num_created': num_created,
                'num_updated': num_updated,
                'last_change_id': last_change_id,
            }

    def save(self, Model, row, columns):

        is_duplicate = False
        is_created = False
        is_updated = False

        # Duplication by tracking values are ignored
        instance = Model.objects.filter(change_id=row.ORA_ROWSCN, row_id=row.ROWID).first()
        is_duplicate = instance is not None
        if instance:
            return is_duplicate, is_created, is_updated

        try:
            pk_values = dict([(col.name, getattr(row, col.ism_name)) for col in columns if col.is_pk])
            instance = Model.objects.get(**pk_values)
            is_updated = True
        except Model.DoesNotExist:
            is_created = True
            instance = Model()

        instance.change_id = row.ORA_ROWSCN
        instance.row_id = row.ROWID
        for col in columns:
            setattr(instance, col.name, getattr(row, col.ism_name))
        instance.save()

        return is_duplicate, is_created, is_updated


    def count_by_change_ids(self, sync_model, change_ids):

        if not change_ids:
            return 0

        query = """
                SELECT
                    COUNT(*) as COUNT
                FROM
                    ISM.{table}
                WHERE
                    ORA_ROWSCN IN ({change_ids})
            """

        sql = query.format(
                table=sync_model.ism_name,
                change_ids=','.join([':p%s' % i for i, v in enumerate(change_ids)])
            )
        params = dict([('p%s' % i, v) for i, v in enumerate(change_ids)])
        return self.exec_query(sql, **params)[0].COUNT


    def get_change_ids(self, sync_model, num_rows, last_change_id):

        query = """
                SELECT
                    DISTINCT ORA_ROWSCN
                FROM (
                    SELECT
                        ORA_ROWSCN
                    FROM (
                        SELECT
                            ORA_ROWSCN
                        FROM
                            ISM.{table}
                        {filter_condition}
                        ORDER BY
                            ORA_ROWSCN ASC
                    )
                    WHERE
                        ROWNUM <= :prownummax
                )
            """
        format_args = {'table': sync_model.ism_name, 'filter_condition': ''}
        params = {'prownummax': num_rows}

        if last_change_id:
            format_args['filter_condition'] = "WHERE ORA_ROWSCN > :prowscn"
            params['prowscn'] = last_change_id

        sql = query.format(**format_args)
        rows = self.exec_query(sql, **params)

        return sorted([row.ORA_ROWSCN for row in rows])


    def fetch_greater_than_last(self, sync_model, columns, change_ids, num_rows, last_change_id=None, last_row_id=None):
        query = """
                SELECT * FROM (
                    SELECT
                        ORA_ROWSCN, ROWID, {fields}
                    FROM
                        ISM.{table}
                    WHERE
                        ORA_ROWSCN IN ({change_ids}) {additional_condition}
                    ORDER BY
                        ORA_ROWSCN ASC, ROWID ASC
                ) WHERE ROWNUM <= :prownummax
            """

        effective_change_ids = [i for i in change_ids if last_change_id is None or i >= last_change_id]

        fields = []
        for col in columns:
            if col.aggregation and '{0}' in col.aggregation:
                fields.append(col.aggregation.format(col.ism_name))
            else:
                fields.append(col.ism_name)

        format_args = {
                'change_ids': ', '.join([':p%s' % i for i, v in enumerate(effective_change_ids)]),
                'fields': ', '.join(fields),
                'table': sync_model.ism_name,
                'additional_condition': '',
            }

        params = {
                'prownummax': num_rows,
                **dict([('p%s' % i, v) for i, v in enumerate(effective_change_ids)])
            }

        if last_change_id and last_row_id:
            # format_args['additional_condition'] = 'AND ORA_ROWSCN >= :prowscn AND ROWID > :prowid'
            format_args['additional_condition'] = 'AND ((ORA_ROWSCN > :prowscn) OR (ORA_ROWSCN = :prowscn AND ROWID > :prowid))'
            params['prowscn'] = last_change_id
            params['prowid'] = last_row_id

        elif last_change_id and last_row_id is None:
            format_args['additional_condition'] = 'AND ORA_ROWSCN > :prowscn'
            params['prowscn'] = last_change_id

        sql = query.format(**format_args)

        return self.exec_query(sql, **params)
