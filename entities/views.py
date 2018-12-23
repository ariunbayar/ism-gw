from collections import defaultdict

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.apps import apps
from django.db import models

from entities.models import SyncModel, SyncModelColumn
from entities.models import SyncStatus
from entities.models import GracefulErrors
from main.utils import connect_db


def all(request):

    sync_models = SyncModel.objects.all()

    context = {
            'sync_models': sync_models,
        }
    return render(request, 'entities/list.html', context)


def get_model_fields(model):
    fields = []

    for field in model._meta.get_fields():
        if isinstance(field, models.AutoField):
            continue
        if field.name == 'row_id':
            continue
        if field.name == 'change_id':
            continue
        fields.append(field)

    return fields


def preview(request, id):

    sync_model = get_object_or_404(SyncModel, pk=id)

    model = sync_model.get_model()

    # Preview values
    preview_titles = ['change_id', 'row_id'] + [f.name for f in get_model_fields(model)]
    preview_values = []
    for instance in model.objects.all().order_by('-change_id', '-row_id')[:10]:
        preview_values.append([getattr(instance, t) for t in preview_titles])

    # SyncStatus for this model
    sync_status_list = sync_model.syncstatus_set.all().order_by('-stopped_at')[:20]

    context = {
            'sync_model': sync_model,
            'preview_titles': preview_titles,
            'preview_values': preview_values,
            'sync_status_list': sync_status_list,
        }
    return render(request, 'entities/preview.html', context)


def _get_pk_constraints(table):

    query = """
        SELECT
            CONSTRAINT_NAME, COLUMN_NAME
        FROM
            ALL_CONS_COLUMNS
        WHERE
            OWNER='ISM' AND TABLE_NAME=:ptable AND
            CONSTRAINT_NAME IN (
                SELECT CONSTRAINT_NAME
                FROM ALL_CONSTRAINTS
                WHERE CONSTRAINT_TYPE='P' AND OWNER='ISM' AND TABLE_NAME=:ptable
            )
    """

    # Ref. about the constraint types: https://docs.oracle.com/database/121/REFRN/GUID-9C96DA92-CFE0-4A3F-9061-C5ED17B43EFE.htm
    with connect_db() as exec_query:
        rows = exec_query(query, ptable=table)

    pk_constraints = defaultdict(list)
    for cons_name, col_name in rows:
        pk_constraints[cons_name].append(col_name)

    return pk_constraints


def track_for_sync(request):

    model_name = request.POST.get('model_name')
    ism_name = request.POST.get('ism_name')

    if SyncModel.objects.filter(model_name=model_name).count():
        return Http404()

    # make sure there is only single primary key constraint
    pk_constraints = _get_pk_constraints(ism_name)
    if len(pk_constraints) > 1:
        graceful_error = GracefulErrors()
        graceful_error.message = "Single primary key constraint required for %s (%s). Got: %s" % (model_name, ism_name, pk_constraints.keys())
        graceful_error.save()
        return Http404()
    else:
        pk_ism_fields = list(pk_constraints.values())[0]

    model = apps.get_model('entities', model_name)

    sync_model = SyncModel()
    sync_model.model_name = model_name
    sync_model.ism_name = ism_name
    sync_model.is_enabled = False
    sync_model.save()
    for field in get_model_fields(model):
        col = SyncModelColumn()
        col.syncmodel = sync_model
        col.name = field.name
        col.ism_name = field.name.upper()[2:]
        col.is_enabled = False
        col.is_pk = col.ism_name in pk_ism_fields
        col.save()

    return redirect('entity-preview', sync_model.id)


def enable_sync_model(request, id):
    sync_model = get_object_or_404(SyncModel, pk=id)
    sync_model.is_enabled = True
    sync_model.save()

    return redirect('entity-preview', sync_model.id)


def disable_sync_model(request, id):
    sync_model = get_object_or_404(SyncModel, pk=id)
    sync_model.is_enabled = False
    sync_model.save()

    return redirect('entity-preview', sync_model.id)


def enable_sync_model_column(request, id):
    sync_column = get_object_or_404(SyncModelColumn, pk=id)
    if sync_column.syncmodel.is_enabled == False:
        sync_column.is_enabled = True
        sync_column.save()

    return redirect('entity-preview', sync_column.syncmodel_id)


def disable_sync_model_column(request, id):
    sync_column = get_object_or_404(SyncModelColumn, pk=id)
    if sync_column.syncmodel.is_enabled == False:
        sync_column.is_enabled = False
        sync_column.save()

    return redirect('entity-preview', sync_column.syncmodel_id)


def delete(request, id):
    sync_model = get_object_or_404(SyncModel, pk=id)

    if sync_column.syncmodel.is_enabled == False:  # if not syncing
        sync_model.columns.all().delete()
        sync_model.syncstatus_set.all().delete()
        sync_model.delete()

    return redirect('entity-list')


def sync_status(request):
    sync_status_list = SyncStatus.objects.all().order_by('-stopped_at')[:20]
    context = {
            'sync_status_list': sync_status_list,
        }
    return render(request, 'entities/sync_status.html', context)


def graceful_errors(request):
    errors = GracefulErrors.objects.all().order_by('-created_at')[:20]

    unread_ids = ','.join([str(e.pk) for e in errors if e.is_read == False])

    context = {
            'errors': errors,
            'unread_ids': unread_ids,
        }
    return render(request, 'entities/graceful_errors.html', context)


def mark_errors_read(request):
    ids = map(int, request.POST.get('ids').split(','))
    if ids:
        GracefulErrors.objects.filter(pk__in=ids).update(is_read=True)

    return redirect('graceful-errors')


def aggregate(request, id):
    sync_model = get_object_or_404(SyncModel, pk=id)
    field_name = request.POST.get('field_name')
    try:
        sync_column = sync_model.columns.get(name=field_name)
    except SyncModelColumn.DoesNotExist:
        error = GracefulErrors()
        error.message = "Can't find %s.%s" % (sync_model.model_name, field_name)
        error.save()
    else:
        sync_column.aggregation = request.POST.get('aggregation') or None
        sync_column.save()

    return redirect('entity-preview', sync_model.id)
