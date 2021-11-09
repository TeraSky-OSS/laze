from abc import abstractmethod


class ConfigEntity():
    @abstractmethod
    def validate(self):
        pass