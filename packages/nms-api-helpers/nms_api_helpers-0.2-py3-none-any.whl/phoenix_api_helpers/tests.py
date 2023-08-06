""" Unit tests for crackle_api_helpers """
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
from __future__ import print_function

import os
import unittest
from collections import namedtuple
from phoenix_api_helpers.api_wrapper import AuthHelpers


class TestHelpers(unittest.TestCase):
    """ Test all helper methods """

    def setUp(self):
        """ Set up tasks for tests """
        apiconfig = namedtuple('apiconfig',
                               'host tenant_id platform_id data_id secret')
        self.config = apiconfig(
            host=os.getenv('host', 'http://staging-api.sdpg.tv'),
            tenant_id=os.getenv('tenant_id', None),
            platform_id=os.getenv('platform_id', None),
            data_id=os.getenv('data_id', None),
            secret=os.getenv('secret', None))

        self.auth_helpers = AuthHelpers(self.config)

    def test_generate_auth_token(self):
        """ Test generate auth token """
        print('testing generate_auth_token')
        self.assertIsNotNone(self.auth_helpers.generate_auth_token())

    def test_register_user(self):
        """ Test generate auth token """
        print('testing register_user')
        status_code, email_address, password, user_id = \
            self.auth_helpers.register_user()
        assert status_code == 201
        assert email_address != ''
        assert password != ''
        assert user_id != ''


if __name__ == '__main__':
    unittest.main()
