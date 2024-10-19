import socket
import can
from pydantic import BaseModel
from typing import Dict
from ruamel.yaml import YAML
import os
import threading
import time
import argparse

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


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

        return cls(uds_services=uds_services)


class UDSModel:
    """
    UDS model class for handling UDS requests with dynamic service mapping.
    using virtual CAN bus. Requires setup of vcan.
    """

    def __init__(
        self,
        config: UDSConfig,
        port,
        tcp_host,
        tcp_port,
        can_interface="vcan0"
    ):
        self.service_map = {
            int(service_id, 16): service.handler
            for service_id, service in config.uds_services.items()
        }
        # Initialize the CAN bus
        self.bus = can.interface.Bus(channel=can_interface, interface="socketcan")
        self.port = port

        # Initialize TCP connection
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.tcp_socket = self.create_tcp_connection()

        threading.Thread(target=self.send_tester_present, daemon=True).start()

    def create_tcp_connection(self):
        """Create a TCP connection to the Windows machine."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.tcp_host, self.tcp_port))
        return sock

    def send_tester_present(self):
        """Periodically send Tester Present and optionally other requests."""
        count = 0
        while True:
            print("Sending 0x3E")
            self.send_request(b"\x3e\x01")  # Tester Present

            count += 1
            time.sleep(5)

    def send_request(self, request):
        """Send a UDS request via CAN and TCP."""
        message = can.Message(
            arbitration_id=0x7DF,  # Standard ID for UDS requests
            data=request,
            is_extended_id=False,
        )
        self.bus.send(message)

        self.tcp_socket.send(request)


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--host-ip", required=True, help="Host IP")
    parser.add_argument("-p", "--host-port", required=True, help="Port to listen on")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    config_file = os.path.join(SCRIPT_DIR, "..", "config", "service_ids.yaml")
    uds_runner = UDSModel(
        config=UDSConfig.from_yaml(config_file),
        tcp_host=args.host_ip,
        tcp_port=args.host_port,
    )
    uds_runner.send_tester_present()
