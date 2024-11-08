from typing import Dict, List, Optional

from pydantic import BaseModel, Field


NRCs = {
    "ServiceNotSupported": 0x12,
    "IncorrectMessageLength": 0x13,
    "IncorrectMessageFormat": 0x14,
    "GeneralProgrammingFailure": 0x21,
    "ProgramMemoryFailure": 0x22,
    "IncorrectDataLengthOrRange": 0x23,
    "RequestOutOfRange": 0x31,
    "SecurityAccessDenied": 0x33,
    "InvalidSession": 0x33,
}


class DTCInfo(BaseModel):
    dtc: int = Field(..., description="Diagnostic Trouble Code")
    status: str = Field(
        ..., description="Status of the DTC (e.g., 'Active', 'Pending', 'Inactive')"
    )


class MemoryBlock(BaseModel):
    adress: int = Field(..., description="Memory adress")
    data: List[int] = Field(
        default_factory=list, description="Data stored at memory adress given"
    )


class Memory(BaseModel):
    memory: Dict[int, MemoryBlock] = Field(default_factory=dict)

    def read_memory(self, adress: int, length: int) -> Optional[List[int]]:
        block = self.memory.get(adress)
        if block:
            return block.data[:length]
        return None

    def write_memory(self, adress: int, data: List[int]) -> None:
        self.memory[adress] = MemoryBlock(adress=adress, data=data)


class _ServiceRequirments(BaseModel):
    name: str
    type: str
    description: str


class Service(BaseModel):
    name: str
    handler: str
    allowed_sessions: List[int]
    length: int
    fields: List[_ServiceRequirments]

    def get_required_fields(self):
        """Returns a dictionary of field names and expected types"""
        return {field.name: field.type for field in self.fields}

    def is_session_valid(self, session_id: int) -> bool:
        """Checks if the given session_id is allowed for this service"""
        return session_id in self.allowed_sessions

    def is_memory_address_valid(self, address: int) -> bool:
        """Checks if the given address is within the service's allowed memory range"""
        if self.memory_range:
            start, end = self.memory_range
            return start <= address <= end
        return True


class ECUState:
    def __init__(
        self,
        identifier_data=None,
        fault_memory=None,
        session_active=False,
        active_session=0x01,
    ):
        self.identifier_data = identifier_data if identifier_data else {}
        self.fault_memory = fault_memory if fault_memory else []
        self.session_active = session_active
        self.active_session = active_session
