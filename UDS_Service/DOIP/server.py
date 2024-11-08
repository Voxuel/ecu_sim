import asyncio
import logging
import can
from UDS_Service.can_service.can_runner import CANBus
from UDS_Service.models.ECU import ECU
from UDS_Service.uds.uds_handler import UDSHandler
from UDS_Service.config.uds_config import load_configuration


logger = logging.getLogger(__name__)

config = load_configuration()

class DoIPServer:
    def __init__(self, host, port=13400, can_interface="vcan0"):
        self.can_interface = can_interface
        self.bus = CANBus(channel=can_interface)
        self.ecu = ECU()
        self.uds_handler = UDSHandler(config=config, ecu=self.ecu)

    async def start(self):
        logger.info("Starting DoIP Server...")
        while True:
            msg = await self.receive_message()
            if msg:
                logger.info("Received message: %s", msg.data.hex())
                response = self.uds_handler.handle_request(msg.data)
                await self.send_response(response)

    async def receive_message(self):
        """Receive a CAN message asynchronously using CANBus."""
        return await self.bus.receive_message()

    async def send_response(self, response_data):
        """Send a CAN response asynchronously."""
        try:
            if isinstance(response_data, can.Message):
                response_bytes = response_data.data
            else:
                response_bytes = response_data


            logger.info("Sent CAN message: %s", response_bytes.hex())
            await self.bus.send_message(0x7E0, response_bytes)

        except Exception as e:
            logger.error("Error sending CAN message: %s", e)

if __name__ == "__main__":
    server = DoIPServer(host="")
    asyncio.run(server.start())