# coding=utf-8
from __future__ import unicode_literals
from .request import Request
from .exceptions import APIException, ConfigException


class ServiceCall(Request):
    __slots__ = ("_sc_api_key", "_sc_voucher_hash", "response_body", "response_header", "status_code")

    def __init__(self, base_url, sc_api_key="", sc_voucher_hash=None):
        super(ServiceCall, self).__init__(base_url)
        self._sc_api_key = sc_api_key
        self._sc_voucher_hash = sc_voucher_hash
        self.status_code = 200
        self.response_header = {}
        self._result = None

    def call(self, service_settings, params=None, sc_api_key="", headers=None,
             sc_voucher_hash=None, internal=True, **kwargs):
        """
        اجرا سرویس ها

        :param dict service_settings:
        :param dict params:
        :param str sc_api_key:
        :param dict headers:
        :param list sc_voucher_hash:
        :param boolean internal:
        """
        self.__validate_service_settings(service_settings)

        if sc_voucher_hash is None:
            sc_voucher_hash = self._sc_voucher_hash or []

        sc_api_key = sc_api_key or self._sc_api_key

        sc_params = {"scProductId": service_settings.get("product_id")}

        if sc_api_key != "":
            sc_params["scApiKey"] = sc_api_key

        if len(sc_voucher_hash) > 0:
            sc_params["scVoucherHash"] = sc_voucher_hash

        if params is None or type(params) is not dict:
            params = sc_params
        else:
            params.update(sc_params)

        url = service_settings.get("sub_url")
        base_url = service_settings.get("base_url")
        method_type = service_settings.get("http_verb", "post")

        self._result = super(ServiceCall, self).call(url=url, base_url=base_url, method=method_type, params=params,
                                                     headers=headers)
        if internal:
            return self._result

        self.__parse_external_services()
        return self.response_body

    @staticmethod
    def __validate_service_settings(service_settings):
        """
        بررسی تنظیمات سرویس

        :param dict service_settings:
        :raise: `ConfigException`
        """
        if "sub_url" not in service_settings:
            raise ConfigException(message="sub_url not set")

        if "base_url" not in service_settings:
            raise ConfigException(message="base_url not set")

        if "product_id" not in service_settings:
            raise ConfigException(message="product_id not set")

    def __parse_external_services(self):
        self.original_result = self._result

        if "header" in self._result:
            self.response_header = self._result["header"]

        if "result" in self._result:
            self.response_body = self._result["result"]

        if "statusCode" in self._result:
            self.status_code = self._result["statusCode"]
            if 300 >= self.status_code < 200:
                raise APIException("Failed to Call API (status code = {})\n{}".format(self.status_code,
                                                                                      self.response_body),
                                   reference_number=super(ServiceCall, self)._reference_number)
