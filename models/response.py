from pydantic import BaseModel, Field
from typing import List, Optional
from models.uds_models import DTCInfo


class UDSServiceResponse(BaseModel):
    service_id: int = Field(..., description="Original Service ID")
    data: Optional[List[int]] = Field(None, description="Response-specific data")

    @property
    def response_id(self):
        return self.service_id + 0x40


class DiagnosticSessionControlResponse(UDSServiceResponse):
    session_status: str = Field(..., description="Current Session Status")


class ECUResetResponse(UDSServiceResponse):
    pass


class ClearDiagnosticInformationResponse(UDSServiceResponse):
    pass


class ReadDTCInformationResponse(UDSServiceResponse):
    dtc_info: List[DTCInfo] = Field(..., description="DTC Information")


class ReadDataByIdentifierResponse(UDSServiceResponse):
    identifier: int = Field(..., description="Data Identifier")
    value: List[int] = Field(..., description="Value")


class ReadMemoryByAddressResponse(UDSServiceResponse):
    address: int = Field(..., description="Memory Address")
    data: List[int] = Field(..., description="Data read from memory")


class WriteDataByIdentifierResponse(UDSServiceResponse):
    pass


class InputOutputControlByIdentifierResponse(UDSServiceResponse):
    pass


class RoutineControlResponse(UDSServiceResponse):
    pass


class RequestDownloadResponse(UDSServiceResponse):
    pass


class RequestUploadResponse(UDSServiceResponse):
    pass


class TransferDataResponse(UDSServiceResponse):
    pass


class RequestTransferExitResponse(UDSServiceResponse):
    pass


class TesterPresentResponse(UDSServiceResponse):
    pass


class ControlDTCSettingResponse(UDSServiceResponse):
    pass


class NegativeResponse(BaseModel):
    response_id: int = Field(0x7F, description="Negative Response ID")
    service_id: int = Field(..., description="Service ID of the request that failed")
    error_code: int = Field(..., description="Specific error code")
