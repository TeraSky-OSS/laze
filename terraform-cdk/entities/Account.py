from .exceptions import InvalidConfigurationParameter, MissingParamException
from .ConfigEntity import ConfigEntity
import validators


class Account(ConfigEntity):
    name = ""
    email = ""
    ou = ""
    roles = []
    policies = []
    network = {}

    # Attributes that will be filled after creation
    id = ""
    provider = ""

    def __init__(self, account_config):
        self._required = ["name", "email", "ou"]
        self._required_network_params = ["name", "vpc_cidr"]
        self._supported_roles = ["audit", "log_archive", "standard"]
        self._config = account_config
        self.__validate()
        
        self.name = self._config["name"]
        self.email = self._config["email"]
        self.ou = self._config["ou"]
        self.roles = self._config["roles"] if "roles" in self._config else []
        self.policies = self._config["policies"] if "policies" in self._config else []
        self.network = self._config["network"] if "network" in self._config and "create" in self._config["network"] and self._config["network"]["create"] == True else {}

    def __validate(self):
        for param in self._required:
            if not param in self._config:
                raise MissingParamException(resource_type='Account', param=param)
        if "network" in self._config and "create" in self._config["network"] and self._config["network"]["create"] == True:
            for net_param in self._required_network_params:
                if not net_param in self._config["network"]:
                    raise MissingParamException(resource_type='AccountNetwork', param=net_param)
        if "roles" in self._config:
            for role in self._config["roles"]:
                if not role in self._supported_roles:
                    raise InvalidConfigurationParameter("roles", self._config["roles"])
        if validators.email(self._config["email"]):
            self.email = self._config["email"]
        else:
            raise InvalidConfigurationParameter("email", self._config["email"])

        print(f'[INFO] Sucessfully validated configuration for account: {self._config["name"]}')