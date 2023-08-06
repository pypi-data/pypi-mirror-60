import requests
from retrying import retry

from fortmatic.api_resources.auth.resource_uris import challenge_get_v1
from fortmatic.api_resources.util.exceptions import APIError
from fortmatic.api_resources.util.request_helpers import get_call_uri
from fortmatic.api_resources.util.request_helpers import get_secret_api_key_headers
from fortmatic.api_resources.util.request_helpers import retry_on_request_exceptions


@retry(
    retry_on_exception=retry_on_request_exceptions,
    wait_exponential_multiplier=100,
    wait_exponential_max=2000,
    stop_max_attempt_number=3,
)
def get_challenge_message_v1(public_address):
    resp = requests.get(
        get_call_uri(challenge_get_v1),
        params={'public_address': public_address},
        headers=get_secret_api_key_headers(),
    )

    data = resp.json()
    if resp.status_code >= 400:
        raise APIError(message=data['message'], error_code=data['error_code'])

    return data['data']['challenge_message']
