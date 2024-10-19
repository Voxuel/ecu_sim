import os
from typing import Dict

from pydantic import BaseModel
from ruamel.yaml import YAML

from models.uds_models import Service


class UDSConfig(BaseModel):
    uds_services: Dict[str, Service]

    @classmethod
    def from_yaml(cls, file: str):
        with open(file, "r") as f:
            yaml = YAML(typ="safe")
            yaml_data = yaml.load(f)
        uds_services = {
            service_id: Service(service_id=service_id, **service_data)
            for service_id, service_data in yaml_data.get("uds_services", {}).items()
        }
        return cls(uds_services=uds_services)


def load_configuration():
    config_file_path = os.path.join(os.getcwd, "service_ids.yaml")
    return UDSConfig.from_yaml(config_file_path)
