# coding=utf-8
import json
from os import path

from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError

from .config import PodConfig
from .exceptions import ConfigException, ServiceCallException, InvalidDataException
from .json_schema import JsonSchemaRules
from .servicecall import ServiceCall


class PodBase(object):
    __config = None
    PRODUCTION_MODE = "PRODUCTION"
    SANDBOX_MODE = "SANDBOX"

    __slots__ = ("_api_token", "_token_issuer", "_server_type", "_request", "_default_params", "_json_schema_rules",
                 "_services_file_path", "_services", "config")

    def __init__(self, api_token, token_issuer="1", server_type="sandbox", config_path=None, sc_api_key="",
                 sc_voucher_hash=None, json_schema_file_path=""):

        self._services = None
        if sc_voucher_hash is None:
            sc_voucher_hash = []

        self._default_params = {
            "sc_voucher_hash": sc_voucher_hash,
            "sc_api_key": sc_api_key
        }

        self._api_token = str(api_token)
        self._token_issuer = str(token_issuer) or "1"

        if len(self._api_token) == 0:
            raise ConfigException("Please set API Token")

        if server_type.lower() == "production" or server_type.lower() == "prod":
            self._server_type = self.PRODUCTION_MODE
        else:
            self._server_type = self.SANDBOX_MODE

        config_path = config_path or path.join(path.abspath(path.dirname(__file__)), 'config.ini')
        self.config = PodConfig(config_path)
        self.__read_service_ids()
        self._request = ServiceCall(self._get_base_url(), sc_api_key=sc_api_key, sc_voucher_hash=sc_voucher_hash)
        self._json_schema_rules = JsonSchemaRules(file_path=json_schema_file_path)

    def _get_base_url(self):
        base_url = self.config.get("base_url", self._server_type)

        if base_url:
            return base_url

        raise ConfigException("Can`t find base_url for {0} mode".format(self._server_type))

    def _get_headers(self):
        """
        :rtype: dict
        """
        return {
            "_token_": self._api_token,
            "_token_issuer_": self._token_issuer
        }

    def total_items(self):
        return self._request.total_items()

    def last_response(self):
        """
        :return: :class:`Response <Response>` object
        :rtype: requests.Response
        """
        return self._request.last_response

    def __read_service_ids(self):
        if self._services is not None:
            return

        with open(self._services_file_path) as services:
            self._services = json.load(services)

    def _get_sc_product_id(self, url, method_type="get"):
        """
        دریافت شناسه سرویس در سرویس کال

        :exception ServiceCallException
        :param str url:
        :param str method_type:
        :return: int
        """
        service = self._get_sc_product_settings(url=url, method_type=method_type)

        return service["product_id"]

    def _get_sc_product_settings(self, url, method_type="get"):
        """
        دریافت تنظیمات سرویس

        :param str url:
        :param str method_type:
        :return: dict
        :exception ServiceCallException
        """
        key = method_type.lower() + url.replace("/", "_")
        if key not in self._services:
            raise ServiceCallException("Can`t find product settings for [{0}] {1} API".format(method_type.upper(), url))

        if "base_url" not in self._services[key]:
            self._services[key]["base_url"] = self.config.get(self._services[key]["platform_url"], self._server_type)

        if self._server_type.lower() not in self._services[key]["products"]:
            raise ServiceCallException("Can`t find service id for [{0}] {1} API".format(method_type.upper(), url))

        self._services[key]["product_id"] = self._services[key]["products"][self._server_type.lower()]
        return self._services[key]

    def _validate(self, document, schema_name):
        """
        :raise
            `jsonschema.exceptions.ValidationError` if the instance
                is invalid

            `jsonschema.exceptions.SchemaError` if the schema itself
                is invalid
        """
        try:
            validate(instance=document, schema=self._json_schema_rules.get_rules(schema_name))
        except ValidationError as e:
            info = {"error_code": 887}
            raise InvalidDataException(message=e.message, **info)
        except SchemaError as e:
            info = {"error_code": 887}
            raise InvalidDataException(message=e.message, **info)

