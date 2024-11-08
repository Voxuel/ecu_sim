from typing import List
from UDS_Service.models.uds_models import DTCInfo, ECUState


class ECU:
    def __init__(self):
        self.state = ECUState(
            fault_memory=[DTCInfo(dtc=0x1234, status="Fault description")],
            session_active=False,
            active_session=0x01,
        )
        self.state.identifier_data = (
            {
                0xF190: b"1HGCM82633A123456",
                0xF186: self.get_active_session(),
                0xF200: b"ECU_Model_1234",
                0xF321: b"1500",
            },
        )

    def get_active_session(self):
        """Get the active session's identifier."""
        if self.state.session_active:
            return bytes(
                [self.state.active_session]
            )
        else:
            return b"\x00"

    def set_active_session(self, session_id):
        """Set a new active session."""
        self.state.session_active = True
        self.state.active_session = session_id
        self.state.identifier_data[0xF186] = bytes(
            [session_id]
        )  

    def reset(self, reset_type: int):
        """Reset the ECU."""
        if reset_type == 0x01:  
            self.state.fault_memory.clear()
            self.state.session_active = False
            self.state.active_session = 0x01  
        elif reset_type == 0x02:  
            self.state = ECUState()  

    def clear_dtc_information(self, identifier: int = None):
        """Clear DTCs (fault memory)."""
        if identifier is None or identifier == 0xFFFFFFFF:
            self.state.fault_memory.clear()  
        else:
            self.state.fault_memory = [
                dtc for dtc in self.state.fault_memory if dtc.dtc != identifier
            ]

    def get_dtc_information(self) -> List[DTCInfo]:
        """Return DTC information."""
        return self.state.fault_memory

    def get_data_by_identifier(self, identifier: int) -> bytes:
        """Retrieve data for a specific identifier."""
        return self.state.identifier_data.get(identifier, b"")

    def write_data_by_identifier(self, identifier: int, data: bytes):
        """Write data to a specific identifier."""
        self.state.identifier_data[identifier] = data
