from .exceptions import InvalidConfigurationParameter, MissingParamException
from .ConfigEntity import ConfigEntity
import validators


class TerraformModule(ConfigEntity):
    name = ""
    source = ""
    version = ""
    variables = {}
    accounts = []

    def __init__(self, tf_module_config):
        self._required = ["name", "source", "accounts"]
        self._config = tf_module_config
        self.__validate()

        self.name = self._config["name"]
        self.source = self._config["source"]
        self.version = self._config["version"] if "version" in self._config else ""
        self.variables = self._config["variables"] if "variables" in self._config else {}
        self.accounts = self._config["accounts"]

    def __validate(self):
        for param in self._required:
            if not param in self._config:
                raise MissingParamException(resource_type='TerraformModule', param=param)

        print(f'[INFO] Sucessfully validated configuration for Terraform module: {self._config["name"]}')