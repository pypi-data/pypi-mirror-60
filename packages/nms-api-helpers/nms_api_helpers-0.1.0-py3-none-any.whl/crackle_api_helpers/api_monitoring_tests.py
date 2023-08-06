""" Unit tests for crackle_api_helpers """
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
from __future__ import print_function
import json
import os
import unittest
from collections import namedtuple
import requests
from crackle_api_helpers.authentication.authentication import (
    Authentication)
from crackle_api_helpers import AuthKeyMissingError, SESSION
from crackle_api_helpers.monitoring.monitoring_wrapper import MonitoringWrapper
from crackle_api_helpers.monitoring.extensions.yaml_parser import YamlParser


class ApiMonitoringHelpers(unittest.TestCase):
    """ Monitor key api end points for failure """
    # pylint: disable=no-member
    email_address, password, user_id = '', '', ''

    def setUp(self):
        """ Set up tasks for monitoring tests """
        self.environment = os.getenv('environment', 'production').lower()
        self.platform = os.getenv('platform', 'html5').lower()
        yaml = YamlParser(
            'crackle_api_helpers/monitoring/platform_config.yaml').data(
                self.environment)[self.platform]
        print('Executing monitoring for {0} on {1} '
              'environment using host {2}\n'.format(
                  self.platform, self.environment, yaml['host']))
        apiconfig = namedtuple('apiconfig',
                               'host partner_id secret geo_code affiliate_id')
        self.configuration = apiconfig(yaml['host'], yaml['partner_id'],
                                       yaml['secret'], yaml['geo_code'],
                                       yaml['affiliate_id'])

    def test_geo_country(self):
        """GET /Service.svc/geo/country"""
        endpoint = '/Service.svc/geo/country'
        auth = Authentication(self.configuration, endpoint)
        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        assert response.status_code == requests.codes.ok

    def test_app_config(self):
        """GET /Service.svc/appconfig"""
        endpoint = '/Service.svc/appconfig'
        auth = Authentication(self.configuration, endpoint)
        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})
        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        assert response.status_code == requests.codes.ok

    def test_genres_all_shows(self):
        """GET /Service.svc/genres/shows/all/US"""
        endpoint = '/Service.svc/genres/shows/all/US?format=json'

        auth = Authentication(self.configuration, endpoint)
        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        assert response.status_code == requests.codes.ok

    def test_genres_all_movies(self):
        """GET /Service.svc/genres/movies/all/US"""
        endpoint = '/Service.svc/genres/movies/all/US?format=json'

        auth = Authentication(self.configuration, endpoint)
        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        assert response.status_code == requests.codes.ok

    def test_app_activation_load(self):
        """POST /Service.svc/externaluser/sso"""
        endpoint = '/Service.svc/externaluser/sso'

        auth = Authentication(self.configuration, endpoint)
        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        data = {
            "AffiliateUserId": self.configuration.affiliate_id,
            "GeoCode": self.configuration.geo_code,
            "PartnerId": self.configuration.partner_id,
            "type": 'auto'
        }
        payload = json.dumps(data)
        response = SESSION.post(path, data=payload)
        assert response.status_code == requests.codes.ok

    def test_homepage_curations(self):
        """GET /Service.svc/curation/preview/homepage/US/1000?format=json"""
        wrapper = MonitoringWrapper(self.configuration)
        response = wrapper.curations('homepage', self.platform, True)
        assert response.status_code == requests.codes.ok
        json_response = json.loads(response.content)
        if json_response['Result']:
            slots = json_response['Result']['Slots']
            curations = [slot['Id'] for slot in slots]
            for curation in curations:
                response = wrapper.curation(curation)
                assert response.status_code == requests.codes.ok

    def test_shows_curations(self):
        """GET /Service.svc/curation/shows/US?format=json"""
        wrapper = MonitoringWrapper(self.configuration)
        response = wrapper.curations('shows', self.platform, True)
        assert response.status_code == requests.codes.ok
        json_response = json.loads(response.content)
        if json_response['Result']:
            slots = json_response['Result']['Slots']
            curations = [slot['Id'] for slot in slots]
            for curation in curations:
                response = wrapper.curation(curation)
                assert response.status_code == requests.codes.ok

    def test_movies_curations(self):
        """GET /Service.svc/curation/movies/US?format=json"""
        wrapper = MonitoringWrapper(self.configuration)
        response = wrapper.curations('movies', self.platform, True)
        assert response.status_code == requests.codes.ok
        json_response = json.loads(response.content)
        if json_response['Result']:
            slots = json_response['Result']['Slots']
            curations = [slot['Id'] for slot in slots]
            for curation in curations:
                response = wrapper.curation(curation)
                assert response.status_code == requests.codes.ok

    def test_details_channel(self):
        """GET /Service.svc/details/channel/2675/US"""
        endpoint = '/Service.svc/details/channel/2675/US'
        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        assert response.status_code == requests.codes.ok

    def test_channel_playlist(self):
        """/Service.svc/channel/2675/playlists/all/US"""
        endpoint = '/Service.svc/channel/2675/playlists/all/US'
        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        assert response.status_code == requests.codes.ok

    def test_media_details(self):
        """/Service.svc/details/media/2509647/US"""
        endpoint = '/Service.svc/details/media/2509647/US'
        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        response = SESSION.get(path)
        assert response.status_code == requests.codes.ok


if __name__ == '__main__':
    unittest.main()
