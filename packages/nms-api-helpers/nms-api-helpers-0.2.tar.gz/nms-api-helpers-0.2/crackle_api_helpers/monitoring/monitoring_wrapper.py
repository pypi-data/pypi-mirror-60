""" Monitoring wrapper class """
from __future__ import print_function
from crackle_api_helpers.authentication.authentication import (
    Authentication)
from crackle_api_helpers import AuthKeyMissingError, SESSION


class MonitoringWrapper:
    """
    Api monitoring methods
    """
    def __init__(self, configuration):
        self.configuration = configuration

    def curations(self, slot='homepage', device_type=None, preview=True):
        """ Returns all curations for a specific slot """
        if device_type == "roku":
            if preview:
                endpoint = '/Service.svc/curation/preview/{0}/US/1000'.format(
                    slot)
            else:
                endpoint = '/Service.svc/curation/{0}/US'.format(
                    slot)
        else:
            endpoint = '/Service.svc/curation/{0}/false/US'.format(
                slot)

        auth = Authentication(self.configuration, endpoint)

        if not auth.key:
            raise AuthKeyMissingError(
                "API access requires generation of an auth key")

        SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        return SESSION.get(path)

    def curation(self, curation_id):
        """ Fetches a curation based on the curation ID """
        endpoint = '/Service.svc/curation/{0}/US'.format(curation_id)

        auth = Authentication(self.configuration, endpoint)
        SESSION.headers.update({'Authorization': auth.key})

        path = '{0}{1}'.format(self.configuration.host, endpoint)
        return SESSION.get(path)
