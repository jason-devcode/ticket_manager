from configparser import ConfigParser
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.environment = None
        self._load_config()

    def _load_config(self):
        self.config = ConfigParser()
        self.config.read(self.config_file)
        self.environment = self.get("env", "ENVIRONMENT")

    def get(self, category, varname):
        return self.config.get(category, varname).replace('"', "")


# Initialize configuration
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / ".config"
config = Config(CONFIG_FILE)
