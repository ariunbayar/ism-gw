from django.core.management.base import BaseCommand
from django.db import connection, models, transaction

from main.utils import execute_query
from entities.models import SyncModel


# NUM_REQUESTS_PER_RUN = 3
NUM_REQUESTS_PER_RUN = 2000


def insert_request_and_children():
    pass


def get_change_ids(table_name, num_rows):
    query = """
            SELECT
                DISTINCT ORA_ROWSCN
            FROM (
                SELECT
                    ORA_ROWSCN
                FROM ISM.{table}
                WHERE
                    ROWNUM <= :prownummax
                ORDER BY
                    ORA_ROWSCN ASC
            )
        """
    sql = query.format(table=table_name)
    columns, rows = execute_query(sql, cache_query=False, prownummax=num_rows)
    return [v for v, in rows]


def fetch(sync_model, change_id):
    query = """
            SELECT
                ROWID, {fields}
            FROM ISM.{table}
            WHERE
                ORA_ROWSCN = :prowscn
        """
    fields = [col.ism_name for col in sync_model.columns.all()]
    sql = query.format(
            fields=', '.join(fields),
            table=sync_model.ism_name,
        )
    import pprint; pprint.pprint(sql)
    import pprint; pprint.pprint(change_id)
    # columns, rows = execute_query(sql, cache_query=False, prowscn=change_id)


class Command(BaseCommand):

    def handle(self, *args, **options):

        sync_models = SyncModel.objects.filter(is_enabled=True)

        last_change_id = 0
        for sync_model in sync_models:
            change_ids = get_change_ids(sync_model.ism_name, NUM_REQUESTS_PER_RUN)

            for change_id in change_ids:
                fetch(sync_model, change_id)
                last_change_id = max(change_id, last_change_id)
