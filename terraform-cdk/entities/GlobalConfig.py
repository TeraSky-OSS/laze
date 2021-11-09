from .exceptions import InvalidConfigurationParameter, MissingParamException
from .ConfigEntity import ConfigEntity
import validators


######################### DEFAULTS #########################
DEFAULT_REGION = 'us-east-1'
DEFAULT_PROFILE = 'default'
DEFAULT_CREATE_ORGANIZATION = True
############################################################


class GlobalConfig(ConfigEntity):
    region = ""
    aws_profile = ""
    create_organization = True
    root_account_alias = ""
    global_tags = {}
    
    def __init__(self, global_config):
        self._required = ["create_organization"]
        self._config = global_config
        self.__validate()
        
        self.region = self._config["region"] if "region" in self._config else DEFAULT_REGION
        self.aws_profile = self._config["aws_profile"] if "aws_profile" in self._config else DEFAULT_PROFILE
        self.create_organization = self._config["create_organization"]
        self.root_account_alias = self._config["root_account_alias"] if "root_account_alias" in self._config else ""
        self.global_tags = self._config["global_tags"] if "global_tags" in self._config else {}

        self._print_info()

    def __validate(self):
        for param in self._required:
            if not param in self._config:
                raise MissingParamException(resource_type='Global Config', param=param)

        print(f'[INFO] Sucessfully validated global configuration')

    def _print_info(self):
        print(f'[INFO] Deploying in region: {self.region}')
        print(f'[INFO] Using AWS profile: {self.aws_profile}')