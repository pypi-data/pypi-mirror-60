from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from fortmatic.django.config import FORTMATIC_IDENTITY_KEY
from fortmatic.django.config import FortmaticAuthBackenMode
from fortmatic.django.exceptions import InvalidChallengeMessage
from fortmatic.django.exceptions import InvalidIdentityToken
from fortmatic.django.exceptions import InvalidSignerAddress
from fortmatic.django.exceptions import PublicAddressDoesNotExist
from fortmatic.django.exceptions import UnsupportedAuthMode
from fortmatic.django.exceptions import UserEmailMissmatch
from fortmatic.utils.auth import get_identity_token_from_header
from fortmatic.utils.auth import PhantomAuth


user_model = get_user_model()


class FortmaticAuthBackend(ModelBackend):

    @staticmethod
    def _load_user_from_email(email):
        try:
            return user_model.objects.get(email=email)
        except user_model.DoesNotExist:
            return None

    @staticmethod
    def _persist_data_in_session(request, identity_token):
        request.session[FORTMATIC_IDENTITY_KEY] = identity_token
        request.session.modified = True

    @staticmethod
    def _validate_identity_token_and_load_user(identity_token, email):
        try:
            PhantomAuth().validate_token(identity_token)
        except (
            InvalidIdentityToken,
            InvalidSignerAddress,
            InvalidChallengeMessage,
        ):
            return None

        public_address = PhantomAuth().get_public_address(identity_token)
        try:
            user = user_model.get_by_public_address(public_address)
        except user_model.DoesNotExist:
            raise PublicAddressDoesNotExist()

        if user.email != email:
            raise UserEmailMissmatch()

        return user

    def user_can_authenticate(self, user):
        if user is None:
            return False

        return super().user_can_authenticate(user)

    def _update_user_with_public_address(self, user, public_address):
        if self.user_can_authenticate(user):
            user.update_user_with_public_address(
                user_id=None,
                public_address=public_address,
                user_obj=user,
            )

    def _handle_phantom_auth(self, request, email):
        identity_token = get_identity_token_from_header(request)
        if identity_token is None:
            return None

        try:
            user = self._validate_identity_token_and_load_user(
                identity_token,
                email,
            )
        except PublicAddressDoesNotExist:
            user = self._load_user_from_email(email)
            if user is None:
                PhantomAuth().invalidate_token(identity_token)
                return None

            self._update_user_with_public_address(
                user,
                PhantomAuth().get_public_address(identity_token),
            )
        except UserEmailMissmatch:
            PhantomAuth().invalidate_token(identity_token)
            return None

        if self.user_can_authenticate(user):
            self._persist_data_in_session(request, identity_token)
            return user

        return None

    def authenticate(
        self,
        request,
        email=None,
        mode=FortmaticAuthBackenMode.PHANTOM,
    ):
        email = user_model.objects.normalize_email(email)

        if mode == FortmaticAuthBackenMode.PHANTOM:
            return self._handle_phantom_auth(request, email)
        else:
            raise UnsupportedAuthMode()
