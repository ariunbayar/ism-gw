import time

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db.models.expressions import RawSQL

from main.utils import connect_db
from entities.models import SyncModel
from entities.models import GracefulErrors


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
                # last_change_id = 8408044588717
                last_row_id = None
                # last_row_id = 'AAAnoRAA4AAJGdDAAA'
                while has_more:
                    rows = self.fetch_greater_than_last(sync_model, columns, NUM_ITEMS_PER_MODEL, last_change_id, last_row_id)
                    if rows:
                        num_compared += len(rows)
                        num_diff_cur, num_missing_cur = self.compare(sync_model, columns, rows)
                        num_diff += num_diff_cur
                        num_missing += num_missing_cur
                        has_more = len(rows) >= NUM_ITEMS_PER_MODEL
                        last_change_id = rows[-1].ORA_ROWSCN
                        last_row_id = rows[-1].ROWID
                    else:
                        break
                    print("... num_compared %s" % num_compared)
                num_extra = sync_model.get_model().objects.all().count() - (num_compared - num_missing)
                print("=== num_compared %s" % num_compared)
                print("=== num_diff     %s" % num_diff)
                print("=== num_missing  %s" % num_missing)
                print("=== num_extra    %s" % num_extra)
                print()

        duration_ms = int(1000 * (time.time() - global_started_at))
        print("Duration {0:,g}".format(duration_ms))

    def compare(self, sync_model, columns, rows):

        def _is_different(row, item):
            return any([v != item[i] for i, v in enumerate(row)])

        fields = [col.name for col in columns]
        Model = sync_model.get_model()

        num_diff = 0
        num_missing = 0
        for row in rows:
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
        return num_diff, num_missing



        min_change_id, min_row_id, *values = rows[0]
        max_change_id, max_row_id, *values = rows[-1]

        qs = sync_model.get_model().objects.filter(row_id__in=[row[1] for row in rows])
        items = qs.values_list('change_id', 'row_id', *fields)[:len(rows)]

        rows = sorted(rows, key=lambda v: v[1])
        items = sorted(items, key=lambda v: v[1])


        iter_rows = iter(rows)
        iter_items = iter(items)



        def _get_next_row():
            try:
                row = next(iter_rows)
            except StopIteration:
                return None, True
            else:
                return row, False

        def _get_next_item():
            try:
                item = next(iter_items)
            except StopIteration:
                return None, True
            else:
                return item, False


        row, is_end_of_rows = _get_next_row()
        item, is_end_of_items = _get_next_item()



        while True:
            # catchup and compare algorithm by admin@example.com 2018-12-21
            if item and row:
                if item[0] == row[0]:
                    if item[1] == row[1]:
                        if _is_different(row[2:], item[2:]):
                            num_diff += 1
                        else:
                            pass
                        row, is_end_of_rows = _get_next_row()
                        item, is_end_of_items = _get_next_item()
                    elif item[1] > row[1]:
                        row, is_end_of_rows = _get_next_row()
                        num_missing += 1
                    elif item[1] < row[1]:
                        item, is_end_of_items = _get_next_item()
                        num_extra += 1
                elif item[0] > row[0]:
                    row, is_end_of_rows = _get_next_row()
                    num_missing += 1
                elif item[0] < row[0]:
                    item, is_end_of_items = _get_next_item()
                    num_extra += 1
            elif is_end_of_rows and is_end_of_items:
                break
            elif is_end_of_rows:
                item, is_end_of_items = _get_next_item()
                num_extra += 1
            elif is_end_of_items:
                row, is_end_of_rows = _get_next_row()
                num_missing += 1

        return num_diff, num_missing, num_extra

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

        format_args = {
                'fields': ', '.join([col.ism_name for col in columns]),
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
