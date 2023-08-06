import requests
import yaml
import os
from pathlib import Path

class BaseClient:
  CONFIG_PATH = Path(f"{str(Path.home())}/.datahen.yml")

  def __init__(self, auth_token = None):
    if 'DATAHEN_TOKEN' in os.environ:
      self._auth_token = os.environ['DATAHEN_TOKEN']
    elif self.CONFIG_PATH.exists():
      with open(self.CONFIG_PATH, 'r') as f:
        try:
          yaml_data = yaml.safe_load(f)
          if 'api_token' in yaml_data:
            self._auth_token = yaml_data['api_token']
          else:
            raise ValueError("Config file exists, but doesn't contain API token")
        except yaml.scanner.ScannerError:
          raise ValueError("Invalid config format")
    elif auth_token is not None:
      self._auth_token = auth_token
    else:
      raise ValueError("Datahen token was not defined")
    
    self._base_headers = {
      "Authorization": f"Bearer {self._auth_token}",
      "Content-Type": "application/json",
    }
    
    self._base_api_url = "https://app.datahen.com/api/v1"

  def get(self, relative_url, params={}):
    url = f"{self._base_api_url}{relative_url}"

    r = requests.get(url, headers=self._base_headers, params=params)

    return r.json()