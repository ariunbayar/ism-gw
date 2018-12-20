"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
import entities.views

urlpatterns = [
    path('entity/list/', entities.views.all, name='entity-list'),
    path('entity/preview/<int:id>/', entities.views.preview, name='entity-preview'),
    path('entity/track/', entities.views.track_for_sync, name='entity-track'),
    path('entity/enable/<int:id>/', entities.views.enable_sync_model, name='sync-model-enable'),
    path('entity/disable/<int:id>/', entities.views.disable_sync_model, name='sync-model-disable'),
    path('entity/enable-column/<int:id>/', entities.views.enable_sync_model_column, name='sync-model-column-enable'),
    path('entity/disable-column/<int:id>/', entities.views.disable_sync_model_column, name='sync-model-column-disable'),
    path('entity/delete/<int:id>/', entities.views.delete, name='entity-delete'),

    path('entity/sync-status/', entities.views.sync_status, name='entity-sync-status'),

    path('entity/graceful-errors/', entities.views.graceful_errors, name='graceful-errors'),
    path('entity/graceful-errors/mark-as-read/', entities.views.mark_errors_read, name='mark-errors-read'),
]
