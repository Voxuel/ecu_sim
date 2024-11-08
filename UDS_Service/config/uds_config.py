import os
from typing import Dict

from pydantic import BaseModel
from ruamel.yaml import YAML

from UDS_Service.models.uds_models import Service

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class UDSConfig(BaseModel):
    uds_services: Dict[int, Service]

    @classmethod
    def from_yaml(cls, file: str = os.path.join(SCRIPT_DIR, "service_ids.yaml")):
        with open(file, "r") as f:
            yaml = YAML(typ="safe")
            yaml_data = yaml.load(f)
        uds_services = {
            service_id: Service(service_id=service_id, **service_data)
            for service_id, service_data in yaml_data.get("uds_services", {}).items()
        }
        return cls(uds_services=uds_services)


def load_configuration():
    config_file_path = os.path.join(
        os.getcwd(), "UDS_Service", "config", "service_ids.yaml"
    )
    return UDSConfig.from_yaml(config_file_path)
