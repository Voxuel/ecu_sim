import os
from pydantic import BaseModel
from typing import Dict
from ruamel.yaml import YAML

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


class Request(BaseModel):
    pass


class Response(BaseModel):
    pass


class Service(BaseModel):
    service_id: str
    service_name: str
    handler: str


class UDSConfig(BaseModel):
    uds_services: Dict[str, Service]

    @classmethod
    def from_yaml(cls, file: str):
        """Load the UDS configuration from a YAML file."""
        with open(file, encoding="utf-8", mode="r") as f:
            yaml_data = YAML(typ="safe").load(f.read())

        # Create Service objects for each entry in the YAML
        uds_services = {
            service_id: Service(service_id=service_id, **service_data)
            for service_id, service_data in yaml_data.get("uds_services", {}).items()
        }

        # Return the UDSConfig instance with the parsed services
        return cls(uds_services=uds_services)
