# copyright 2019 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

__docformat__ = "restructuredtext en"

from random import randrange
from hashlib import sha512
from requests import get as requests_get

from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from saml2.client import Saml2Client
from saml2.config import Config
from saml2.entity import BINDING_HTTP_POST as ENTITY_BINDING_HTTP_POST

from cubicweb import NoResultError
from cubicweb.server import DEBUG


def get_user(request):
    """ Retrieve posted user informations from database
    """
    if not request.POST or 'SAMLResponse' not in request.POST:
        return None

    config = request.registry['cubicweb.config']

    subject, identity = retrieve_identity_from_client(
        config, request.POST['SAMLResponse'])
    if not subject:
        return None

    with request.registry['cubicweb.repository'].internal_cnx() as cnx:
        try:
            user = cnx.execute('Any U WHERE U is CWUser, '
                               '            U login %(userid)s',
                               {'userid': subject}).one().eid
        except NoResultError:
            user = None

    return user


def register_user(request):
    if not request.POST or 'SAMLResponse' not in request.POST:
        return None

    config = request.registry['cubicweb.config']

    subject, identity = retrieve_identity_from_client(
        config, request.POST['SAMLResponse'])
    if not subject:
        return None

    default_group = config.get('saml-register-default-group', 'guests')

    with request.registry['cubicweb.repository'].internal_cnx() as cnx:
        try:
            cnx.execute('Any G WHERE G is CWGroup, '
                        '            G name "%(group)s"',
                        {'group': default_group}).one()

            password = ''
            if config.get(
               'saml-register-default-password', 'empty') == 'random':
                password = generate_hash(subject)

            user = cnx.execute('INSERT CWUser U: U login "%(login)s",'
                               '                 U upassword "%(password)s",'
                               '                 U in_group G',
                               '           WHERE G name "%(group)s"',
                               {
                                   'login': subject,
                                   'password': password,
                                   'group': default_group,
                               }).one().eid
            cnx.commit()

        except NoResultError:
            user = None

    return user


def generate_hash(config, *args):
    hash_value = sha512()

    for element in args:
        hash_value.update(str(element))

    hash_value.update('{6:d}'.format(randrange(1, pow(10, 6))))

    return hash_value.hexdigest()


def get_metadata_from_uri(metadata_uri):
    """ Retrieve metadata xml content
    """

    if metadata_uri.startswith('file://'):
        with open(metadata_uri[7:], 'rb') as pipe:
            metadata = pipe.read()

        return metadata

    elif metadata_uri:
        return requests_get(metadata_uri).text

    return ''


def build_base_url(config):
    """ Generate base_url from cubicweb config and ensure this URL ends with a
    slash
    """
    base_url = config.get('base-url', '')
    if not base_url.endswith('/'):
        base_url += '/'

    return base_url


def saml_client(config):
    """ Generate a SAML client from all-in-one.conf metadata
    """
    cubicweb_sources = config.read_sources_file()

    if 'saml' not in cubicweb_sources:
        raise KeyError(
            "saml: Cannot found 'saml' section in cubicweb sources file")

    elif 'saml-metadata-uri' not in cubicweb_sources['saml']:
        raise KeyError(
            "saml: Cannot found 'saml-metadata-uri' option in saml section")

    base_url = build_base_url(config)

    settings = {
        'debug': bool(DEBUG),
        'entityid': cubicweb_sources['saml'].get('saml-entity-id', ''),
        'metadata': {
            'inline': [
                get_metadata_from_uri(
                    cubicweb_sources['saml']['saml-metadata-uri'])
            ],
        },
        'service': {
            'sp': {
                'endpoints': {
                    'assertion_consumer_service': [
                        (base_url + 'saml', BINDING_HTTP_POST),
                        (base_url + 'saml', BINDING_HTTP_REDIRECT),
                    ],
                },
                'allow_unsolicited':
                    config.get('saml-allow-unsolicited', True),
                'authn_requests_signed':
                    config.get('saml-authn-requests-signed', False),
                'logout_requests_signed':
                    config.get('saml-logout-requests-signed', True),
                'want_assertions_signed':
                    config.get('saml-want-assertions-signed', True),
                'want_response_signed':
                    config.get('saml-want-response-signed', False),
            },
        },
    }

    configuration = Config()
    configuration.allow_unknown_attributes = True
    configuration.load(settings)

    return Saml2Client(config=configuration)


def retrieve_url_from_client(config, request):
    """ Generate SAML URL from metadata informations
    """
    reqid, info = saml_client(config).prepare_for_authenticate(
        relay_state=get_relay_state_from_request(config, request))

    # Select the IdP URL to send the AuthN request to
    return dict(info['headers']).get('Location', '')


def retrieve_identity_from_client(config, request):
    """ Retrieve identity from posted data
    """
    authn_response = saml_client(config).parse_authn_request_response(
        request, ENTITY_BINDING_HTTP_POST)

    if authn_response:
        subject = authn_response.get_subject()
        if subject:
            subject = subject.text

        return subject, authn_response.get_identity()

    return None, {}


def get_relay_state_from_request(config, request):
    """ Generate relay state where the user should be returned after
    successfull login
    """
    if request.GET:
        return request.GET.get('postlogin_path', '')

    elif request.POST:
        base_url = build_base_url(config)
        return request.POST.get('__errorurl', '').replace(base_url, '')

    return ''
