from typing import List

from models.response import DTCInfo
from models.uds_models import ECUState


class ECU:
    def __init__(self):
        self.state = ECUState(
            identifier_data={
                0xF190: b"1HGCM82633A123456",  # Example: VIN
                0xF123: b"\x01\x02\x03\x04",  # Example: some other data
            }
        )

    def reset(self, reset_type: int):
        if reset_type == 0x01:  # Soft reset
            self.state.fault_memory.clear()
            self.state.session_active = False
            self.state.active_session = 0x01
        elif reset_type == 0x02:  # Hard reset
            self.state = ECUState()

    def clear_dtc_information(self, identifier: int = None):
        if identifier is None or identifier == 0xFFFFFFFF:
            self.state.fault_memory.clear()
        else:
            if identifier in self.state.fault_memory:
                del self.state.fault_memory[identifier]

    def get_dtc_information(self) -> List[DTCInfo]:
        return [
            DTCInfo(dtc=dtc, status=status)
            for dtc, status in self.state.fault_memory.items()
        ]

    def get_data_by_identifier(self, identifier: int) -> bytes:
        return self.state.identifier_data.get(identifier)

    def write_data_by_identifier(self, identifier: int, data: bytes):
        self.state.identifier_data[identifier] = data
