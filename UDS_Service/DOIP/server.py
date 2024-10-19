import argparse
import asyncio
import logging

from can_service.can_runner import CANBus
from uds.uds_handler import UDSHandler

from config.uds_config import load_configuration

logger = logging.getLogger(__name__)

config = load_configuration()


class DoIPServer:
    def __init__(self, host, port=13400, can_interface="vcan0"):
        self.can_interface = can_interface
        self.bus = CANBus(channel=can_interface)
        self.uds_handler = UDSHandler(config=config)

    async def start(self):
        logger.info("Starting DoIP Server...")
        while True:
            msg = await self.receive_message()
            if msg:
                logger.info("Received message: %s", msg.data.hex())
                await self.handle_request(msg.data)

    async def receive_message(self):
        """Receive a CAN message asynchronously using CANBus."""
        return await self.bus.receive_message()

    async def handle_request(self, data):
        response = self.uds_handler.handle_request(data)
        await self.send_response(response)

    async def send_response(self, response_data):
        """Send a CAN response asynchronously."""
        await self.bus.send_message(0x7E0, response_data)
        logger.info("Sent CAN message: %s", response_data.hex())

    async def handle_session_control(self, data):
        sub_function = data[2]
        self.ecu_state.session_active = True
        self.ecu_state.active_session = sub_function
        logger.info("Switching to session: %s", hex(sub_function))
        await asyncio.sleep(0)  # Simulate some asynchronous operation
        return b"\x03\x50" + bytes([sub_function])

    async def handle_tester_present(self, data):
        if self.ecu_state.session_active:
            logger.info("Session is active, responding with Tester Present")
            return b"\x02\x7e\x3e"
        else:
            return self.negative_response(0x3E, 0x7F)

    async def handle_read_data_by_identifier(self, data):
        identifier = (data[2] << 8) | data[3]
        if identifier == 0xF190:  # VIN ID
            vin_data = b"1HGCM82633A123456"
            logger.info("Responding with VIN")
            await asyncio.sleep(0)
            return b"\x10" + vin_data

    def negative_response(self, service_id, error_code):
        """Return a negative response for UDS requests."""
        return b"\x03\x7f" + bytes([service_id]) + bytes([error_code])


def _parser_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-h", "--host-IP", required=True, help="IP of the host machine")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parser_args()
    server = DoIPServer(host=args.host_IP)
    asyncio.run(server.start())
