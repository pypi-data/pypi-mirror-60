# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google ID Token helpers.

Provides support for verifying `OpenID Connect ID Tokens`_, especially ones
generated by Google infrastructure.

To parse and verify an ID Token issued by Google's OAuth 2.0 authorization
server use :func:`verify_oauth2_token`. To verify an ID Token issued by
Firebase, use :func:`verify_firebase_token`.

A general purpose ID Token verifier is available as :func:`verify_token`.

Example::

    from google.oauth2 import id_token
    from google.auth.transport import requests

    request = requests.Request()

    id_info = id_token.verify_oauth2_token(
        token, request, 'my-client-id.example.com')

    if id_info['iss'] != 'https://accounts.google.com':
        raise ValueError('Wrong issuer.')

    userid = id_info['sub']

By default, this will re-fetch certificates for each verification. Because
Google's public keys are only changed infrequently (on the order of once per
day), you may wish to take advantage of caching to reduce latency and the
potential for network errors. This can be accomplished using an external
library like `CacheControl`_ to create a cache-aware
:class:`google.auth.transport.Request`::

    import cachecontrol
    import google.auth.transport.requests
    import requests

    session = requests.session()
    cached_session = cachecontrol.CacheControl(session)
    request = google.auth.transport.requests.Request(session=cached_session)

.. _OpenID Connect ID Token:
    http://openid.net/specs/openid-connect-core-1_0.html#IDToken
.. _CacheControl: https://cachecontrol.readthedocs.io
"""

import json

from six.moves import http_client

from google.auth import exceptions
from google.auth import jwt

# The URL that provides public certificates for verifying ID tokens issued
# by Google's OAuth 2.0 authorization server.
_GOOGLE_OAUTH2_CERTS_URL = "https://www.googleapis.com/oauth2/v1/certs"

# The URL that provides public certificates for verifying ID tokens issued
# by Firebase and the Google APIs infrastructure
_GOOGLE_APIS_CERTS_URL = (
    "https://www.googleapis.com/robot/v1/metadata/x509"
    "/securetoken@system.gserviceaccount.com"
)


def _fetch_certs(request, certs_url):
    """Fetches certificates.

    Google-style cerificate endpoints return JSON in the format of
    ``{'key id': 'x509 certificate'}``.

    Args:
        request (google.auth.transport.Request): The object used to make
            HTTP requests.
        certs_url (str): The certificate endpoint URL.

    Returns:
        Mapping[str, str]: A mapping of public key ID to x.509 certificate
            data.
    """
    response = request(certs_url, method="GET")

    if response.status != http_client.OK:
        raise exceptions.TransportError(
            "Could not fetch certificates at {}".format(certs_url)
        )

    return json.loads(response.data.decode("utf-8"))


def verify_token(id_token, request, audience=None, certs_url=_GOOGLE_OAUTH2_CERTS_URL):
    """Verifies an ID token and returns the decoded token.

    Args:
        id_token (Union[str, bytes]): The encoded token.
        request (google.auth.transport.Request): The object used to make
            HTTP requests.
        audience (str): The audience that this token is intended for. If None
            then the audience is not verified.
        certs_url (str): The URL that specifies the certificates to use to
            verify the token. This URL should return JSON in the format of
            ``{'key id': 'x509 certificate'}``.

    Returns:
        Mapping[str, Any]: The decoded token.
    """
    certs = _fetch_certs(request, certs_url)

    return jwt.decode(id_token, certs=certs, audience=audience)


def verify_oauth2_token(id_token, request, audience=None):
    """Verifies an ID Token issued by Google's OAuth 2.0 authorization server.

    Args:
        id_token (Union[str, bytes]): The encoded token.
        request (google.auth.transport.Request): The object used to make
            HTTP requests.
        audience (str): The audience that this token is intended for. This is
            typically your application's OAuth 2.0 client ID. If None then the
            audience is not verified.

    Returns:
        Mapping[str, Any]: The decoded token.
    """
    return verify_token(
        id_token, request, audience=audience, certs_url=_GOOGLE_OAUTH2_CERTS_URL
    )


def verify_firebase_token(id_token, request, audience=None):
    """Verifies an ID Token issued by Firebase Authentication.

    Args:
        id_token (Union[str, bytes]): The encoded token.
        request (google.auth.transport.Request): The object used to make
            HTTP requests.
        audience (str): The audience that this token is intended for. This is
            typically your Firebase application ID. If None then the audience
            is not verified.

    Returns:
        Mapping[str, Any]: The decoded token.
    """
    return verify_token(
        id_token, request, audience=audience, certs_url=_GOOGLE_APIS_CERTS_URL
    )
