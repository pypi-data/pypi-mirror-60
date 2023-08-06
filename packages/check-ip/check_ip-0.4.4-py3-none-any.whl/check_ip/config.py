from dataclasses import dataclass
from typing import List

import yaml


class ConfigError(Exception):
    """Raised when there is a problem with the configuration."""


@dataclass
class Config:
    email: str
    api_key: str
    zone: str
    records: List[str]
    verbose: bool = False

    @property
    def record_names(self):
        return [f"{record}.{self.zone}" for record in self.records]

    @classmethod
    def from_file(cls, filepath):
        try:
            with open(filepath, "r") as f:
                _config = yaml.safe_load(f)
        except FileNotFoundError as err:
            raise ConfigError(f"Config file not found: '{filepath}'") from err
        try:
            config = cls(**_config)
        except TypeError as err:
            raise ConfigError("Config file is missing values.") from err
        return config
