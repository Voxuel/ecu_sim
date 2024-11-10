import asyncio
import can


async def send_uds_request():
    bus = can.interface.Bus(channel="vcan0", interface="socketcan")

    async def send_request(msg):
        bus.send(msg)
        print("Sent UDS request:", msg)

        while True:
            response = bus.recv()
            if response:
                print("Received response:", response)
                return response

    print("\nChecking current session:")
    current_session_request = can.Message(
        arbitration_id=0x7E0, data=[0x22, 0xF1, 0x86, 0x00], is_extended_id=False
    )
    current_session_response = await send_request(current_session_request)
    print(f"Current session: {current_session_response.data.hex()}")

    print("\nChanging to Prog Diagnostic Session (0x10 0x02):")
    change_session_request = can.Message(
        arbitration_id=0x7E0, data=[0x10, 0x02], is_extended_id=False
    )
    change_session_response = await send_request(change_session_request)
    print(f"Change session response: {change_session_response.data.hex()}")

    print("\nChecking session after change:")
    new_session_response = await send_request(current_session_request)
    print(f"New session: {new_session_response.data.hex()}")


if __name__ == "__main__":
    asyncio.run(send_uds_request())
