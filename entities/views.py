from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.apps import apps
from django.db import models

from entities.models import SyncModel, SyncModelColumn


def list(request):

    sync_models = SyncModel.objects.all()

    context = {
            'sync_models': sync_models,
        }
    return render(request, 'entities/list.html', context)


def preview(request, id):

    sync_model = get_object_or_404(SyncModel, pk=id)

    context = {
            'sync_model': sync_model,
        }
    return render(request, 'entities/preview.html', context)


def track_for_sync(request):

    model_name = request.POST.get('model_name')
    ism_name = request.POST.get('ism_name')

    if SyncModel.objects.filter(model_name=model_name).count():
        return Http404()

    model = apps.get_model('entities', model_name)

    sync_model = SyncModel()
    sync_model.model_name = model_name
    sync_model.ism_name = ism_name
    sync_model.is_enabled = False
    sync_model.save()

    for field in model._meta.get_fields():
        if isinstance(field, models.AutoField):
            continue
        if field.name == 'row_id':
            continue
        if field.name == 'change_id':
            continue
        col = SyncModelColumn()
        col.syncmodel = sync_model
        col.name = field.name
        col.ism_name = field.name.upper()[2:]
        col.is_enabled = False
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
