import logging

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

LOGGER = logging.getLogger(__name__)


class RhasspyError(Exception):
    pass


class RhasspyAPI:
    def __init__(self, url):
        self.session = Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "accept": "application/json"}
        )
        self.base_url = url

        retries = Retry(backoff_factor=1)
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        LOGGER.info("Trying to connect to Rhasspy...")
        try:
            self.get("/api/version")
        except requests.exceptions.ConnectionError as error:
            raise Exception(
                f"Unable to connect to rhasspy server at {url} - "
                "Ensure it is running and try again!"
            )

    def get(self, url):
        response = self.session.get(f"{self.base_url}{url}")
        if response.status_code == 500 and response.text:
            raise RhasspyError(response.text)
        response.raise_for_status()
        if response.headers["content-type"] == "application/json":
            return response.json()

    def post(self, url, body=None):
        response = self.session.post(f"{self.base_url}{url}", json=body)
        if response.status_code == 500 and response.text:
            raise RhasspyError(response.text)
        response.raise_for_status()
        if response.headers["content-type"] == "application/json":
            return response.json()