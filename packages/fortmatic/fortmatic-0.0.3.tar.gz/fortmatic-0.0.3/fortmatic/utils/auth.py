import base64
import json

from eth_account.messages import encode_structured_data
from web3.auto import w3

from fortmatic.api_resources.auth.challenge_message import get_challenge_message_v1
from fortmatic.api_resources.auth.invalidate_token import invalidate_token_v1
from fortmatic.django.exceptions import InvalidChallengeMessage
from fortmatic.django.exceptions import InvalidIdentityToken
from fortmatic.django.exceptions import InvalidSignerAddress
from fortmatic.utils.http import parse_authorization_header


def get_identity_token_from_header(request):
    return parse_authorization_header(request)


class PhantomAuth:

    def __init__(self):
        pass

    @staticmethod
    def decode_token(identity_token):
        """
        Args:
            identity_token (base64.str): Base64 encoded string.

        Raises:
            InvalidIdentityToken: If token is malformed.
        """
        try:
            decoded_dat = json.loads(
                base64.urlsafe_b64decode(
                    identity_token,
                ).decode('utf-8'),
            )
        except Exception:
            raise InvalidIdentityToken()

        proof = decoded_dat[0]
        claim = decoded_dat[1]
        return proof, claim

    def _check_integratity_and_authenticity_of_the_token(
        self,
        identity_token,
    ):
        """
        Args:
            identity_token (base64.str): Base64 encoded string.

        Raises:
            InvalidSignerAddress: If unable to match recovered address with
                signer address.
        """
        proof, claim = self.decode_token(identity_token)
        signable_message = encode_structured_data(claim)
        recovered_address = w3.eth.account.recover_message(
            signable_message,
            signature=proof,
        )

        if recovered_address != claim['message']['addr']:
            raise InvalidSignerAddress()

    def _check_validity_of_the_token(self, identity_token):
        """
        Args:
            identity_token (base64.str): Base64 encoded string.

        Raises:
            InvalidChallengeMessage: If challenge message in ``identity_token``
                does not match API provided challenge message.
        """
        _, claim = self.decode_token(identity_token)
        if claim['message']['chmsg'] != self.get_challenge_message(identity_token):
            raise InvalidChallengeMessage()

    def validate_token(
        self,
        identity_token,
        skip_checking_challenge_message=False,
    ):
        """
        Args:
            identity_token (base64.str): Base64 encoded string.

        Returns:
            None.
        """
        self._check_integratity_and_authenticity_of_the_token(identity_token)
        self._check_validity_of_the_token(identity_token)

    def get_public_address(self, identity_token):
        """
        Args:
            identity_token (base64.str): Base64 encoded string.

        Raises:
            InvalidIdentityToken: If token is malformed.
        """
        self._check_integratity_and_authenticity_of_the_token(identity_token)

        _, claim = self.decode_token(identity_token)
        try:
            return claim['message']['addr']
        except KeyError:
            raise InvalidIdentityToken()

    def get_challenge_message(self, identity_token):
        return get_challenge_message_v1(
            self.get_public_address(identity_token),
        )

    def invalidate_token(self, identity_token):
        invalidate_token_v1(self.get_public_address(identity_token))

    def invalidate_token_by_public_address(self, public_address):
        invalidate_token_v1(public_address)
