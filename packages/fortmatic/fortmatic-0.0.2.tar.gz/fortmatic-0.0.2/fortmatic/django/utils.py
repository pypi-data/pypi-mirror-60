from django.contrib.auth import logout as django_logout

from fortmatic.django.config import FORTMATIC_IDENTITY_KEY
from fortmatic.utils.auth import PhantomAuth


def logout(request):
    identity_token = request.session.get(FORTMATIC_IDENTITY_KEY, None)
    if identity_token:
        PhantomAuth().invalidate_token(identity_token)

    django_logout(request)
