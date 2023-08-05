import requests

from pyptax import settings


class Ptax:
    base_url = settings.SERVICE_URL

    def __init__(self, resource):
        self.resource = resource

    def _perform_request(self):
        url = f"{self.base_url}{self.resource.path}"
        response = requests.get(url, params=self.resource.params)
        return response.json()

    def _parse_data(self, raw_data):
        return self.resource.parse(raw_data)

    def response(self):
        raw_data = self._perform_request()
        return self._parse_data(raw_data)
