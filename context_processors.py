from django.conf import settings
from entities.models import GracefulErrors


def main_context_processor(request):

    return {
        'num_graceful_errors': GracefulErrors.objects.filter(is_read=False).count(),
    }
