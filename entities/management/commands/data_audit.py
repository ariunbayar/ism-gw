import time
import sys

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.utils import timezone

from main.utils import connect_db
from entities.models import SyncModel
from entities.models import GracefulErrors
from ism.models import LongQuery


NUM_ITEMS_PER_MODEL = 100000


class Command(BaseCommand):

    def exec_query(self, *args, **kwargs):
        started_at = time.time()
        result = self._exec_query(*args, **kwargs)
        duration_ms = int((time.time() - started_at) * 1000)
        if duration_ms > 5000:
            q = LongQuery()
            q.query = args[0].strip()
            q.args = json.dumps(kwargs)
            q.duration_ms = duration_ms
            q.save()

        return result

    def handle(self, *args, **options):

        global_started_at = time.time()

        sync_models = SyncModel.objects.filter(is_enabled=True)
        sync_models = sync_models.filter(ism_name='T_PSP_ALN_M')

        with connect_db() as exec_query:
            self._exec_query = exec_query

            for sync_model in sync_models:
                print('=== Starting with %s (%s)' % (sync_model.model_name, sync_model.ism_name))
                columns = sync_model.columns.filter(is_enabled=True)
                num_compared = 0
                num_diff = 0
                num_missing = 0
                num_extra = 0
                has_more = True
                last_change_id = None
                last_row_id = None
                # last_change_id = 8408044588717
                # last_row_id = 'AAAnoRAA4AAJGdDAAA'

                while has_more:
                    print('fetching since (%s, %s)' % (last_change_id, last_row_id))
                    sys.stdout.flush()
                    rows_iter = self.fetch_greater_than_last(sync_model, columns, NUM_ITEMS_PER_MODEL, last_change_id, last_row_id)
                    print('comparing')
                    sys.stdout.flush()
                    num_compared_cur, num_diff_cur, num_missing_cur, last_change_id, last_row_id = self.compare(sync_model, columns, rows_iter)
                    num_compared += num_compared_cur
                    num_diff += num_diff_cur
                    num_missing += num_missing_cur
                    has_more = num_compared_cur >= NUM_ITEMS_PER_MODEL
                    print("... num_compared {0:,g}".format(num_compared_cur))
                    print("... num_diff {0:,g}".format(num_diff_cur))
                    print("... num_missing {0:,g}".format(num_missing_cur))
                    sys.stdout.flush()

                num_extra = sync_model.get_model().objects.all().count() - (num_compared - num_missing)
                print("=== num_compared %s" % num_compared)
                print("=== num_diff     %s" % num_diff)
                print("=== num_missing  %s" % num_missing)
                print("=== num_extra    %s" % num_extra)
                print()
                sync_model.audited_at = timezone.now()
                sync_model.audit_result = (
                    "num_compared {0}\n"
                    "num_diff     {1}\n"
                    "num_missing  {2}\n"
                    "num_extra    {3}\n"
                ).format(
                    num_compared,
                    num_diff,
                    num_missing,
                    num_extra,
                )
                sync_model.save()

        duration_ms = int(1000 * (time.time() - global_started_at))
        print("Duration {0:,g}".format(duration_ms))

    def compare(self, sync_model, columns, rows_iter):

        def _is_different(row, item):
            return any([v != item[i] for i, v in enumerate(row)])

        fields = [col.name for col in columns]
        Model = sync_model.get_model()

        num_diff = 0
        num_missing = 0
        num_compared = 0
        last_change_id = None
        last_row_id = None
        for row in rows_iter:
            qs = Model.objects.filter(change_id=row[0], row_id=row[1])
            items = list(qs.values_list(*fields))
            num_items = len(items)
            if num_items < 1:
                print("[Missing] %r" % (row,))
                num_missing += 1
            elif num_items > 1:
                graceful_error = GracefulErrors()
                graceful_error.message = "Found duplication while auditing %s, %s" % (row[0], row[1])
                graceful_error.save()
            else:
                if _is_different(row[2:], items[0]):
                    num_diff += 1
            num_compared += 1
            last_change_id = row[0]
            last_row_id = row[1]

        return num_compared, num_diff, num_missing, last_change_id, last_row_id


    def fetch_greater_than_last(self, sync_model, columns, num_rows, last_change_id=None, last_row_id=None):

        query = """
                SELECT * FROM (
                    SELECT
                        ORA_ROWSCN, ROWID, {fields}
                    FROM
                        ISM.{table}
                    {condition}
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
                'condition': '',
            }

        params = {'prownummax': num_rows}

        if last_change_id and last_row_id:
            format_args['condition'] = 'WHERE (ORA_ROWSCN > :prowscn) OR (ORA_ROWSCN = :prowscn AND ROWID > :prowid)'
            params['prowscn'] = last_change_id
            params['prowid'] = last_row_id

        sql = query.format(**format_args)

        return self.exec_query(sql, **params)
