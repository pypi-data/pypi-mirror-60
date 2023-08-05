# coding=utf-8
from __future__ import unicode_literals
from sys import version_info


class PodException(Exception):
    __slots__ = ("message", "error_code")

    def __init__(self, message, *args, **kwargs):
        self.message = message
        self.error_code = kwargs.pop("error_code", 0)
        super(Exception, self).__init__(*args)

    def __str__(self):
        if version_info[0] > 2:
            return "Error {}\nError Code {}".format(self.message, self.error_code)

        return ("Error {}\nError Code {}".format(self.message, self.error_code)).encode("utf-8")


class InvalidDataException(PodException):
    pass


class HTTPException(PodException):
    __slots__ = ("status_code", "raw_result")

    def __init__(self, *args, **kwargs):
        self.status_code = kwargs.pop("status_code", None)
        self.raw_result = kwargs.pop("raw_result", None)
        message = kwargs.pop("message", "")

        super(HTTPException, self).__init__(message, *args, **kwargs)

    def __str__(self):
        if version_info[0] > 2:
            return "{} (Status Code : {})".format(self.message, self.status_code)

        return ("{} (Status Code : {})".format(self.message, self.status_code)).encode("utf-8")


class APIException(PodException):
    __slots__ = "reference_number"

    def __init__(self, message, **kwargs):
        self.reference_number = kwargs.pop("reference_number", "")

        super(APIException, self).__init__(message, **kwargs)

    def __str__(self):
        if version_info[0] > 2:
            return "{}\nReference Number : {}\nError Code : {}".format(self.message, self.reference_number,
                                                                       self.error_code)

        return ("{}\nReference Number : {}\nError Code : {}".format(self.message, self.reference_number,
                                                                    self.error_code)).encode("utf-8")


class ConfigException(PodException):
    pass


class ServiceCallException(PodException):
    pass


class NotFoundException(PodException):
    pass
