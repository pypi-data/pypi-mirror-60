""" Phoenix API Wrapper """
# pylint: disable=too-few-public-methods,no-member,too-many-lines
# pylint: disable=super-init-not-called,too-many-locals
# pylint: disable=too-many-arguments

from __future__ import print_function
from collections import namedtuple
import json
from crackle_api_helpers.authentication.authentication_helpers import (
    generate_username)
from phoenix_api_helpers import SESSION


class AuthHelpers:
    """
    Authentication methods
    """

    def __init__(self, configuration=None):
        if not all(configuration):
            raise Exception(
                "Missing one or all of the required environment"
                " variables: tenant_id, platform_id, data_id, secret")
        self.configuration = configuration

    def generate_auth_token(self):
        """
        Generate the auth token
        :return: the token value
        """
        endpoint = '/user/auth/clients/login?api-version=1.0'
        path = '{0}{1}'.format(self.configuration.host, endpoint)
        SESSION.headers.update(
            {'x-venue-tenantid': self.configuration.tenant_id,
             'x-venue-platformid': self.configuration.platform_id,
             'x-venue-locale': 'en-US',
             'Access-Control-Request-Method': 'POST',
             'Access-Control-Request-Headers': 'api-tenant-key,content-type',
             'Origin': 'http://localhost:4200'})

        data = {
            "id": self.configuration.data_id,
            "secret": self.configuration.secret
        }
        payload = json.dumps(data)
        response = SESSION.post(path, data=payload)
        try:
            response_text = json.loads(response.content)
            if response_text['status'] == 200:
                return response_text['data']['token']
            return None
        except ValueError as exception:
            print(exception)

    def register_user(self, **kwargs):
        """
        POST http://staging-api.sdpg.tv/user/auth/clients/login?api-version=1.0
        optional args: prefix, email_domain,
              password, firstname, lastname, email_address
        on success:
            return data(message_code, email_address, password, user_id)
        on failure:
            return data(message_code, "", "", "", "")

        """
        endpoint = '/user/users/register?api-version=1.0'
        path = '{0}{1}'.format(self.configuration.host, endpoint)
        auth_token = self.generate_auth_token()
        bearer_token = 'Bearer ' + auth_token

        if not auth_token:
            raise Exception("API access requires generation of an auth token")

        SESSION.headers.update(
            {'x-venue-tenantid': self.configuration.tenant_id,
             'x-venue-platformid': self.configuration.platform_id,
             'x-venue-locale': 'en-US',
             'Authorization': bearer_token})

        prefix = kwargs.get('prefix', 'phoenixbddautomation+AUTO_JAN_API_')
        email_address = kwargs.get('email_address', None)
        password = kwargs.get('password', 'kyqkuBmn4')
        first_name = kwargs.get('first_name', 'autoRandom1')
        last_name = kwargs.get('last_name', 'autoRandom2')
        if email_address is None:
            email_domain = kwargs.get('email_domain', 'gmail.com')
            email_address = generate_username(prefix) + '@' + email_domain

        data = {
            "email": email_address,
            "password": password,
            "firstName": first_name,
            "lastName": last_name
        }
        payload = json.dumps(data)
        response = SESSION.post(path, data=payload)
        try:
            data = namedtuple(
                "data", ["status_code", "email", "password", "user_id"])
            response_text = json.loads(response.content)
            if response_text['status'] == 201:
                user_id = response_text['data']['user']['id']
                return data(response_text['status'], email_address, password, user_id)
            return data(response_text['status'], "", "", "")
        except ValueError as exception:
            print(exception)
