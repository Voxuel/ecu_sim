from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DTCInfo(BaseModel):
    dtc: str = Field(..., description="Diagnostic Trouble Code")
    status: str = Field(
        ..., description="Status of the DTC (e.g., 'Active', 'Pending', 'Inactive')"
    )


class MemoryBlock(BaseModel):
    adress: int = Field(..., description="Memory adress")
    data = List[int] = Field(
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


class Service(BaseModel):
    name: str
    handler: str
    allowed_sessions: List[int]


class ECUState(BaseModel):
    session_active: bool = Field(default=False, description="Is session active")
    active_session: str = Field(
        default="0x01", description="Active session for diagnostic commands"
    )
    fault_memory: List[DTCInfo] = Field(default_factory=dict, description="DTC Info")
    identifier_data: Dict[int, bytes] = Field(
        default_factory=dict, description="Data storage for identifier"
    )
    memory: Memory = Field(default_factory=Memory)
