import json
from .wom_logger import WOMLogger
from .rest_client import RestClient


class RegistryProxy(object):

    def __init__(self, base_url, public_key):
        self.PublicKey = public_key
        self.client = RestClient(base_url)
        self.__logger = WOMLogger("Registry")

    def voucher_create(self, source_id, nonce, payload):
        request_payload = json.dumps({'SourceId': source_id,
                                      'Nonce': nonce,
                                      'Payload': payload})
        self.__logger.debug(request_payload)

        return self.client.voucher_create(request_payload)

    def voucher_verify(self, payload):
        request_payload = json.dumps({'Payload': payload})
        self.__logger.debug(request_payload)

        return self.client.voucher_verify(request_payload)

    def payment_register(self, source_id, nonce, payload):
        request_payload = json.dumps({'PosId': source_id,
                                      'Nonce': nonce,
                                      'Payload': payload})
        self.__logger.debug(request_payload)

        return self.client.payment_register(request_payload)

    def payment_verify(self, payload):
        request_payload = json.dumps({'Payload': payload})
        self.__logger.debug(request_payload)

        return self.client.payment_verify(request_payload)
