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

from mock import patch
from pyramid import testing

from cubicweb import ValidationError
from cubicweb.devtools import testlib

from cubicweb_saml.utils import (build_base_url,
                                 generate_hash,
                                 get_user,
                                 register_user)


class SAMLUtilsTC(testlib.CubicWebTC):

    def setUp(self):
        super(SAMLUtilsTC, self).setUp()

        self.request = testing.DummyRequest(post={'SAMLResponse': ''})
        self.request.registry['cubicweb.config'] = self.config
        self.request.registry['cubicweb.repository'] = self.repo

    def test_build_base_url(self):
        config = self.vreg.config

        self.assertEqual(
            build_base_url(config), 'http://testing.fr/cubicweb/')

        config['base-url'] = 'http://url.without.backslash'

        self.assertEqual(
            build_base_url(config), 'http://url.without.backslash/')

    def test_generate_hash(self):
        self.assertNotEqual(generate_hash('example'),
                            generate_hash('example'))

        self.assertIsNotNone(generate_hash('example', 'with', 'arguments'))

    def test_get_an_unknown_user(self):
        with patch('cubicweb_saml.utils.retrieve_identity_from_client',
                   return_value=('unknown_user', {})):

            self.assertIsNone(get_user(self.request))

    def test_get_an_existing_user(self):
        with self.admin_access.repo_cnx() as cnx:
            user = self.create_user(cnx, 'saml_user')

            with patch('cubicweb_saml.utils.retrieve_identity_from_client',
                       return_value=('saml_user', {})):

                userid = get_user(self.request)

                self.assertEqual(userid, user.eid)

    def test_register_a_new_user(self):
        with patch('cubicweb_saml.utils.retrieve_identity_from_client',
                   return_value=('saml_user', {})):

            self.assertIsNone(get_user(self.request))

            userid = register_user(self.request)

            self.assertIsNotNone(userid)
            self.assertEqual(get_user(self.request), userid)

    def test_register_an_existing_user(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, 'saml_user')

            with patch('cubicweb_saml.utils.retrieve_identity_from_client',
                       return_value=('saml_user', {})):

                self.assertIsNotNone(get_user(self.request))

                with self.assertRaises(ValidationError):
                    register_user(self.request)


if __name__ == '__main__':
    from unittest import main
    main()
