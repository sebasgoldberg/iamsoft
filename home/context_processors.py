from django.conf import settings

def ambiente(request):
    """
    Devuelve los datos del ambiente
    """
    return {'ambiente': settings.AMBIENTE }
