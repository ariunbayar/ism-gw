from datetime import timedelta

from django.shortcuts import render
from django.utils.timezone import localtime, now

from entities.models import SyncModel
from collections import namedtuple


def _populate_sync_models(objs):

    nt_sync_model = namedtuple('SyncModel', 'id is_ok model_name ism_name is_enabled last_change_id last_sync_at')
    ok_date = localtime(now()) - timedelta(minutes=5)

    def _to_namedtuple(sync_model, nt_builder):
        if sync_model.last_sync_at is None:
            is_ok = False
        else:
            is_ok = sync_model.last_sync_at > ok_date

        return nt_builder(
                id=sync_model.id,
                is_ok=is_ok,
                model_name=sync_model.model_name,
                ism_name=sync_model.ism_name,
                is_enabled=sync_model.is_enabled,
                last_change_id=sync_model.last_change_id,
                last_sync_at=sync_model.last_sync_at,
            )

    for obj in objs:
        yield _to_namedtuple(obj, nt_sync_model)


def dashboard(request):

    qs = SyncModel.objects.all()

    if request.GET.get('disabled') == '0':
        qs = qs.filter(is_enabled=True)

    context = {
            'sync_models': _populate_sync_models(qs.order_by('model_name')),
        }
    return render(request, "ism/dashboard.html", context)
