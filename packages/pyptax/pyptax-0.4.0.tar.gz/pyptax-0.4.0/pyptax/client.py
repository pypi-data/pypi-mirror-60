import requests

from pyptax import settings
from pyptax.exceptions import ClientError


class Ptax:
    base_url = settings.SERVICE_URL

    def __init__(self, resource):
        self.resource = resource

    def _perform_request(self):
        url = f"{self.base_url}{self.resource.path}"
        response = requests.get(url, params=self.resource.params)
        if not response.ok:
            raise ClientError("Could not retrieve information from Ptax Service")
        return response.json()

    def _parse_data(self, raw_data):
        return self.resource.parse(raw_data)

    def response(self):
        raw_data = self._perform_request()
        return self._parse_data(raw_data)
