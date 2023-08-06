import requests
import sys
from .wom_logger import WOMLogger


class RestClient:
    headers = {'Content-type': 'application/json'}
    __logger = WOMLogger("RestClient")

    def __init__(self, base_url):
        self.__base_url = base_url

    @classmethod
    def __post_request(cls, payload, url):
        try:
            r = requests.post(url, data=payload, headers=RestClient.headers)
            cls.__logger.debug("POST {url}  STATUS {code}".format(url=url, code=r.status_code))
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as err:
            cls.__logger.error(err)
            sys.exit(1)

    @classmethod
    def __post_command(cls, payload, url):
        try:
            r = requests.post(url, data=payload, headers=RestClient.headers)
            cls.__logger.debug("POST {url}  STATUS {code}".format(url=url, code=r.status_code))
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            cls.__logger.error(err)
            sys.exit(1)

    def voucher_create(self, payload):
        url = self.__base_url + "/voucher/create"

        return RestClient.__post_request(payload, url)

    def voucher_verify(self, payload):
        url = self.__base_url + "/voucher/verify"

        RestClient.__post_command(payload, url)

    def payment_register(self, payload):
        url = self.__base_url + "/payment/register"

        return RestClient.__post_request(payload, url)

    def payment_verify(self, payload):
        url = self.__base_url + "/payment/verify"

        RestClient.__post_command(payload, url)
