import time
from datetime import datetime

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection, models, transaction

from main.utils import connect_db
from entities.models import SyncModel
from entities.models import SyncStatus


# NUM_ITEMS_PER_MODEL = 3
NUM_ITEMS_PER_MODEL = 2000


class Command(BaseCommand):

    def exec_query(self, *args, **kwargs):
        print(args[0])
        import pprint; pprint.pprint(kwargs)
        return self._exec_query(*args, **kwargs)

    def handle(self, *args, **options):

        started_at = time.time()

        last_change_id = 0
        sync_models = SyncModel.objects.filter(is_enabled=True)
        for sync_model in sync_models:

            with transaction.atomic():
                with connect_db() as exec_query:
                    self._exec_query = exec_query

                    num_fetched, last_change_id = self.fetch_since(sync_model, NUM_ITEMS_PER_MODEL, last_change_id)
                    print('Last change id %s' % last_change_id)

        sync_status = SyncStatus()
        sync_status.sync_model = None
        sync_status.duration_ms = int(1000 * (time.time() - started_at))
        sync_status.save()

    def fetch_since(self, sync_model, num_rows, last_change_id):

        Model = sync_model.get_model()

        change_ids = self.get_change_ids(sync_model, num_rows)
        columns = sync_model.columns.filter(is_enabled=True)


        num_fetch_expected = self.count_by_change_ids(sync_model, change_ids)

        num_fetched = 0
        num_duplicates = 0
        num_created = 0

        last_row_id = None

        while num_fetched < num_fetch_expected:
            rows = self.fetch_greater_than_last(sync_model, columns, change_ids, num_rows, last_change_id, last_row_id)

            for row in rows:
                is_duplicate, is_created = self.save(Model, row, columns)
                print('*', end="")
                num_fetched += 1
                num_created += 1 if is_created else 0
                num_duplicates += 1 if is_duplicate else 0
                last_change_id = row.ORA_ROWSCN
                last_row_id = row.ROWID

        print("Num fetch expected: %s" % num_fetch_expected)
        print("Num fetched: %s" % num_fetched)
        print("Num duplicates: %s" % num_duplicates)
        print("Num created: %s" % num_created)
        print("Num updated: %s" % (num_fetched - num_created))

        return num_fetched, last_change_id

    def save(self, Model, row, columns):

        is_duplicate = False
        is_created = False

        # Duplication by tracking values are ignored
        instance = Model.objects.filter(change_id=row.ORA_ROWSCN, row_id=row.ROWID).first()
        is_duplicate = instance is not None
        if instance:
            return is_duplicate, is_created

        try:
            pk_values = dict([(col.name, getattr(row, col.ism_name)) for col in columns if col.is_pk])
            instance = Model.objects.get(**pk_values)
        except Model.DoesNotExist:
            is_created = True
            instance = Model()
            instance.change_id = row.ORA_ROWSCN
            instance.row_id = row.ROWID

        for col in columns:
            setattr(instance, col.name, getattr(row, col.ism_name))
        instance.save()

        return is_duplicate, is_created


    def count_by_change_ids(self, sync_model, change_ids):

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


    def get_change_ids(self, sync_model, num_rows):

        query = """
                SELECT
                    DISTINCT ORA_ROWSCN
                FROM (
                    SELECT
                        ORA_ROWSCN
                    FROM ISM.{table}
                    WHERE
                        ROWNUM <= :prownummax
                )
            """
        sql = query.format(table=sync_model.ism_name)
        rows = self.exec_query(sql, prownummax=num_rows)

        return sorted([row.ORA_ROWSCN for row in rows])


    def fetch_greater_than_last(self, sync_model, columns, change_ids, num_rows, last_change_id=None, last_row_id=None):
        query = """
                SELECT * FROM (
                    SELECT
                        ORA_ROWSCN, ROWID, {fields}
                    FROM
                        ISM.{table}
                    WHERE
                        ORA_ROWSCN IN ({change_ids})
                        {additional_condition}
                    ORDER BY
                        ORA_ROWSCN ASC, ROWID ASC
                ) WHERE ROWNUM <= :prownummax
            """

        effective_change_ids = [i for i in change_ids if i >= last_change_id]

        format_args = {
                'change_ids': ', '.join([':p%s' % i for i, v in enumerate(effective_change_ids)]),
                'fields': ', '.join([col.ism_name for col in columns]),
                'table': sync_model.ism_name,
                'additional_condition': '',
            }

        params = {
                'prownummax': num_rows,
                **dict([('p%s' % i, v) for i, v in enumerate(effective_change_ids)])
            }

        if last_change_id and last_row_id:
            format_args['additional_condition'] = 'AND ORA_ROWSCN >= :prowscn AND ROWID > :prowid'
            params['prowscn'] = last_change_id
            params['prowid'] = last_row_id

        elif last_change_id and last_row_id is None:
            format_args['additional_condition'] = 'AND ORA_ROWSCN > :prowscn'
            params['prowscn'] = last_change_id

        sql = query.format(**format_args)

        return self.exec_query(sql, **params)
