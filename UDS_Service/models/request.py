from typing import List, Optional

from pydantic import BaseModel, Field


class UDSServiceRequest(BaseModel):
    service_id: int = Field(..., description="Service ID")
    data: Optional[List[int]] = Field(default=None, description="Service-specific data")
    session_id: int = Field(..., description="Session ID for the request")


class DiagnosticSessionControlRequest(UDSServiceRequest):
    service_id: int = Field(
        0x10, description="Service ID for Diagnostic Session Control"
    )
    session_type: int = Field(..., description="Session Type")


class ECUResetRequest(UDSServiceRequest):
    service_id: int = Field(0x11, description="Service ID for ECU Reset")
    reset_type: int = Field(..., description="Type of ECU Reset")


class ClearDiagnosticInformationRequest(UDSServiceRequest):
    service_id: int = Field(
        0x14, description="Service ID for Clear Diagnostic Information"
    )
    identifier: int = Field(..., description="Diagnostic Identifier to clear")


class ReadDTCInformationRequest(UDSServiceRequest):
    service_id: int = Field(0x19, description="Service ID for Read DTC Information")


class ReadDataByIdentifierRequest(UDSServiceRequest):
    service_id: int = Field(0x22, description="Service ID for Read Data By Identifier")
    identifier: int = Field(..., description="Data Identifier")


class ReadMemoryByAddressRequest(UDSServiceRequest):
    service_id: int = Field(0x23, description="Service ID for Read Memory By Address")
    address: int = Field(..., description="Memory address to read")
    length: int = Field(..., description="Number of bytes to read")


class WriteDataByIdentifierRequest(UDSServiceRequest):
    service_id: int = Field(0x2E, description="Service ID for Write Data By Identifier")
    identifier: int = Field(..., description="Data Identifier to write")
    data: List[int] = Field(..., description="Data to write")


class InputOutputControlByIdentifierRequest(UDSServiceRequest):
    service_id: int = Field(
        0x2F, description="Service ID for Input Output Control By Identifier"
    )
    identifier: int = Field(..., description="Control Identifier")
    control: int = Field(..., description="Control command")


class RoutineControlRequest(UDSServiceRequest):
    service_id: int = Field(0x31, description="Service ID for Routine Control")
    routine_id: int = Field(..., description="ID of the routine to control")
    action: int = Field(..., description="Action to perform (start/status/stop)")


class RequestDownloadRequest(UDSServiceRequest):
    service_id: int = Field(0x34, description="Service ID for Request Download")
    memory_address: int = Field(..., description="Memory address to download to")
    data_length: int = Field(..., description="Length of the data")


class RequestUploadRequest(UDSServiceRequest):
    service_id: int = Field(0x35, description="Service ID for Request Upload")
    memory_address: int = Field(..., description="Memory address to upload from")
    data_length: int = Field(..., description="Length of the data")


class TransferDataRequest(UDSServiceRequest):
    service_id: int = Field(0x36, description="Service ID for Transfer Data")
    data: List[int] = Field(..., description="Data to transfer")


class RequestTransferExitRequest(UDSServiceRequest):
    service_id: int = Field(0x37, description="Service ID for Request Transfer Exit")


class TesterPresentRequest(UDSServiceRequest):
    service_id: int = Field(0x3E, description="Service ID for Tester Present")


class ControlDTCSettingRequest(UDSServiceRequest):
    service_id: int = Field(0x85, description="Service ID for Control DTC Setting")
    setting_type: int = Field(..., description="Setting type")
    value: int = Field(..., description="Setting value")
