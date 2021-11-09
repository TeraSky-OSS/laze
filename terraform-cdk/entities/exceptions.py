from .errors import *


class MissingParamException(Exception):

    def __init__(self, resource_type, param):
        self._resource_type = resource_type
        self._param = param

    def __str__(self):
        return f'{ERR_MSG_MISSING_PARAM} [Resource type: {self._resource_type}, Parameter: {self._param}]'

class InvalidConfigurationParameter(Exception):

    def __init__(self, key, value):
        self._key = key
        self._value = value

    def __str__(self):
        return f'{ERR_MSG_INVALID_CONFIG} <{self._key} : {self._value}>'