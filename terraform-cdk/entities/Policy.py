from .exceptions import InvalidConfigurationParameter, MissingParamException
from .ConfigEntity import ConfigEntity
import validators
import json
import os
import sys


class Policy(ConfigEntity):
    name = ""
    type = ""
    content = ""

    # Attributes that will be filled after creation
    id = ""
    
    def __init__(self, policy_config):
        self._required = ["name", "type"]
        self._config = policy_config
        self.__validate()
        
        self.name = self._config["name"]
        self.type = self._config["type"]
        self.content = self.get_policy_content()

    def __validate(self):
        for param in self._required:
            if not param in self._config:
                raise MissingParamException(resource_type='Policy', param=param)
        if "content_inline" not in self._config and "content_from_file" not in self._config:
            raise MissingParamException(resource_type='Policy', param='"content_inline" or "content_from_file"')

        print(f'[INFO] Sucessfully validated configuration for policy: {self._config["name"]}')

    def get_policy_content(self):
        config_rel_path=os.path.dirname(os.environ.get("CONFIG_FILE_PATH"))
        
        if "content_inline" in self._config:
            return json.dumps(json.loads(self._config["content_inline"])) # Read the string as JSON and convert to string
        elif "content_from_file" in self._config:
            try:
                with open(f'{config_rel_path}/{self._config["content_from_file"]}', 'r') as f:
                    return json.dumps(json.load(f)) # Read the file as JSON and convert to string
            except FileNotFoundError as e:
                print(e)
                sys.exit(2)