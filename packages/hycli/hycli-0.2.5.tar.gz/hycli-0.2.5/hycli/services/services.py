import requests

from halo import Halo

from .requests import request_token


class Services(object):
    def __init__(self, endpoint_env, username, password):
        """
        TODO: put correct endpoints to check if online
        extractor: '/'
        vat_validator: https://github.com/hypatos/vat-validator/pull/36
        """
        self.extractor_endpoint = None
        self.vat_validator_endpoint = None
        self.validation_endpoint = None
        self.token_endpoint = None

        self.create_endpoints(endpoint_env)
        self.services_up = self.are_up()
        if endpoint_env != "localhost":
            self.token = request_token(self.token_endpoint, username, password)
        else:
            self.token = None

    def are_up(self):
        """ Return True if all endpoints are up. """
        endpoints = [
            self.extractor_endpoint,
            self.vat_validator_endpoint,
            self.validation_endpoint,
        ]

        up = all([self.is_up(endpoint) for endpoint in endpoints if endpoint])

        return up

    def is_up(self, endpoint):
        """ Return True if 401 code was received, else return False. """
        endpoint_spinner = Halo(spinner="dots")
        try:
            req = requests.get(endpoint)

        # On connection error, return False.
        except requests.exceptions.ConnectionError:
            fail_msg = f"Service on endpoint {endpoint} is offline\n"
            endpoint_spinner.fail(fail_msg)
            return False

        # Connection was successful, return True on 405, else return False.
        else:
            if req.status_code == 401 or req.status_code == 405:
                endpoint_spinner.succeed(f"{endpoint} endpoint is online\n")
                return True
            fail_msg = f"{endpoint} endpoint returns {req.status_code}\n"
            endpoint_spinner.fail(fail_msg)
            return False

    def create_endpoints(self, endpoint_env):
        """ Creates the endpoint addresses for the correct endpoint env """
        if endpoint_env == "production":
            self.extractor_endpoint = "https://api.hypatos.ai/v2/subscription/invoices"
            self.vat_validator_endpoint = None
            self.token_endpoint = "https://customers.hypatos.ai/auth/realms/hypatos/protocol/openid-connect/token"
        elif endpoint_env == "staging":
            self.extractor_endpoint = "https://api.stage.hypatos.ai/v2/extract"
            self.vat_validator_endpoint = None
            self.token_endpoint = "https://customers.stage.hypatos.ai/auth/realms/hypatos/protocol/openid-connect/token"
        else:
            self.extractor_endpoint = "http://localhost:8000/v2/extract"
            self.vat_validator_endpoint = "http://localhost:7000/validate"
            self.validation_endpoint = "http://localhost:7001/validate"
