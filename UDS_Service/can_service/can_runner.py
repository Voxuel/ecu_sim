import can
import asyncio
from logging import getLogger

logger = getLogger(__name__)


class CANBus:
    def __init__(self, channel="vcan0", timeout=None):
        self.bus = can.interface.Bus(channel=channel, interface="socketcan")
        self.timeout = timeout

    async def send_message(self, arbitration_id: int, data: bytearray):
        """Send a CAN message asynchronously."""
        try:
            message = can.Message(
                arbitration_id=arbitration_id, data=data, is_extended_id=False
            )
            await asyncio.get_event_loop().run_in_executor(None, self.bus.send, message)
            logger.info("Sent CAN message: %s", message)
        except Exception as e:
            logger.error("Error sending CAN message: %s", e)

    async def receive_message(self):
        """Receive a CAN message asynchronously."""
        try:
            loop = asyncio.get_event_loop()
            message = await loop.run_in_executor(None, self.bus.recv, self.timeout)
            if message:
                logger.info("Received CAN message: %s", message)
                return message
            else:
                logger.warning("No CAN message received (timeout).")
                return None
        except Exception as e:
            logger.error("Error receiving CAN message: %s", e)

    def close(self):
        """Clean up the CAN bus resources."""
        self.bus.shutdown()
        logger.info("CAN bus shutdown successfully.")

    def __enter__(self):
        """Context manager for CAN bus."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Ensure proper CAN bus shutdown when exiting context."""
        self.close()
