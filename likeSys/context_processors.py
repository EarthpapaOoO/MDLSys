# likeSys/context_processors.py
from django.conf import settings

def target_url(request):
    return {'TARGET_URL': getattr(settings, 'TARGET_URL', '')}
