from .exceptions import InvalidConfigurationParameter, MissingParamException
from .ConfigEntity import ConfigEntity
import validators


class OrganizationlUnit(ConfigEntity):
    name = ""
    policies = []
    parent_ou = ""

    # Attributes that will be filled after creation
    id = ""

    def __init__(self, ou_config):
        self._required = ["name"]
        self._config = ou_config
        self.__validate()
        
        self.name = self._config["name"]
        self.policies = self._config["policies"] if "policies" in self._config else []
        self.parent_ou = self._config["parent_ou"] if "parent_ou" in self._config else ""

    def __validate(self):
        for param in self._required:
            if not param in self._config:
                raise MissingParamException(resource_type='OrganizationalUnit', param=param)

        print(f'[INFO] Sucessfully validated configuration for organizational unit: {self._config["name"]}')