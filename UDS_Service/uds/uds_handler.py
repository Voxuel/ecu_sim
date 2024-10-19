from logging import getLogger

from pydantic import ValidationError

from models.ECU import ECU
from models.request import (
    ClearDiagnosticInformationRequest,
    ControlDTCSettingRequest,
    DiagnosticSessionControlRequest,
    ECUResetRequest,
    InputOutputControlByIdentifierRequest,
    ReadDataByIdentifierRequest,
    ReadDTCInformationRequest,
    ReadMemoryByAddressRequest,
    RequestDownloadRequest,
    RequestTransferExitRequest,
    RequestUploadRequest,
    RoutineControlRequest,
    TesterPresentRequest,
    TransferDataRequest,
    WriteDataByIdentifierRequest,
)
from models.response import (
    ClearDiagnosticInformationResponse,
    ControlDTCSettingResponse,
    DiagnosticSessionControlResponse,
    ECUResetResponse,
    InputOutputControlByIdentifierResponse,
    NegativeResponse,
    ReadDataByIdentifierResponse,
    ReadDTCInformationResponse,
    ReadMemoryByAddressResponse,
    RequestDownloadResponse,
    RequestTransferExitResponse,
    RequestUploadResponse,
    RoutineControlResponse,
    TesterPresentResponse,
    TransferDataResponse,
    WriteDataByIdentifierResponse,
)
from models.uds_models import ECUState

logger = getLogger(__name__)


class UDSHandler:
    def __init__(self, config):
        self.service_map = {
            int(service_id, 16): service.handler
            for service_id, service in config.uds_services.items()
        }
        self.current_session = 0x01  # Default to Default Session
        self.ecu = ECU()

        # Create a mapping of service IDs to request models
        self.request_model_map = {
            0x10: DiagnosticSessionControlRequest,
            0x11: ECUResetRequest,
            0x14: ClearDiagnosticInformationRequest,
            0x19: ReadDTCInformationRequest,
            0x22: ReadDataByIdentifierRequest,
            0x23: ReadMemoryByAddressRequest,
            0x2E: WriteDataByIdentifierRequest,
            0x2F: InputOutputControlByIdentifierRequest,
            0x31: RoutineControlRequest,
            0x34: RequestDownloadRequest,
            0x35: RequestUploadRequest,
            0x36: TransferDataRequest,
            0x37: RequestTransferExitRequest,
            0x3E: TesterPresentRequest,
            0x85: ControlDTCSettingRequest,
        }

    def handle_request(self, request: bytes):
        service_id = request[1]
        try:
            # Validate the session for the service
            if service_id in self.service_map:
                handler_function = getattr(self, self.service_map[service_id], None)
                if handler_function:
                    request_data = self.deserialize_request(service_id, request)
                    return handler_function(request_data)
            return self.negative_response(service_id, 0x11)  # Service Not Supported
        except ValidationError:
            return self.negative_response(
                service_id, 0x13
            )  # Incorrect Message Length or Invalid Format

    def is_session_allowed(self, service_id: int) -> bool:
        allowed_sessions = self.service_map[service_id].allowed_sessions
        return (
            self.ecu.state.active_session in allowed_sessions
            and self.ecu.state.session_active
        )

    def deserialize_request(self, service_id, request):
        """Deserialize the request into the corresponding model using the request model map."""
        model = self.request_model_map.get(service_id)
        if model:
            return model.parse_obj(self.extract_request_data(service_id, request))
        raise ValueError("Unsupported service ID.")

    def extract_request_data(self, service_id, request):
        """Extract relevant fields from the request for deserialization."""
        if service_id == 0x10:  # Diagnostic Session Control
            return {
                "service_id": service_id,
                "session_type": request[2],
                "data": request[3:],
            }
        elif service_id == 0x11:  # ECU Reset
            return {
                "service_id": service_id,
                "reset_type": request[2],
                "data": request[3:],
            }
        elif service_id == 0x14:  # Clear Diagnostic Information
            return {
                "service_id": service_id,
                "identifier": request[2],
                "data": request[3:],
            }
        elif service_id == 0x19:  # Read DTC Information
            return {"service_id": service_id, "data": request[2:]}
        elif service_id == 0x22:  # Read Data By Identifier
            return {
                "service_id": service_id,
                "identifier": (request[2] << 8) | request[3],
                "data": request[4:],
            }
        elif service_id == 0x23:  # Read Memory By Address
            return {
                "service_id": service_id,
                "address": (request[2] << 8) | request[3],
                "length": request[4],
                "data": request[5:],
            }
        elif service_id == 0x2E:  # Write Data By Identifier
            return {
                "service_id": service_id,
                "identifier": (request[2] << 8) | request[3],
                "data": list(request[4:]),
            }
        elif service_id == 0x2F:  # Input Output Control By Identifier
            return {
                "service_id": service_id,
                "identifier": (request[2] << 8) | request[3],
                "control": request[4],
                "data": request[5:],
            }
        elif service_id == 0x31:  # Routine Control
            return {
                "service_id": service_id,
                "routine_id": (request[2] << 8) | request[3],
                "action": request[4],
                "data": request[5:],
            }
        elif service_id == 0x34:  # Request Download
            return {
                "service_id": service_id,
                "memory_address": (request[2] << 8) | request[3],
                "data_length": request[4],
                "data": request[5:],
            }
        elif service_id == 0x35:  # Request Upload
            return {
                "service_id": service_id,
                "memory_address": (request[2] << 8) | request[3],
                "data_length": request[4],
                "data": request[5:],
            }
        elif service_id == 0x36:  # Transfer Data
            return {"service_id": service_id, "data": list(request[2:])}
        elif service_id == 0x37:  # Request Transfer Exit
            return {"service_id": service_id, "data": request[2:]}
        elif service_id == 0x3E:  # Tester Present
            return {"service_id": service_id, "data": request[2:]}
        elif service_id == 0x85:  # Control DTC Setting
            return {
                "service_id": service_id,
                "setting_type": request[2],
                "value": request[3],
                "data": request[4:],
            }
        else:
            raise ValueError("Unsupported service ID.")

    def handle_diagnostic_session_control(
        self, request: DiagnosticSessionControlRequest
    ):
        if request.session_type in self.service_map[0x10]["allowed_sessions"]:
            self.current_session = request.session_type
            return DiagnosticSessionControlResponse(
                response_id=0x10,
                session_status=f"Session {hex(self.current_session)} active",
            )
        else:
            return self.negative_response(0x10, 0x7E)  # Request Out of Range

    def reset_ecu_simulation(self):
        """Reinitialize all ECU states to their default values."""
        self.ecu.state = ECUState()
        logger.info("ECU simulation has been reset.")

    def handle_ecu_reset(self, request: ECUResetRequest):
        if not self.is_session_allowed(request.service_id):
            return self.negative_response(request.service_id, 0x7E)
        if request.reset_type == 0x01:
            logger.info("Performing soft ECU reset...")
            self.ecu.state.fault_memory.clear()
            self.ecu.state.session_active = False
            self.ecu.state.active_session = "0x01"
        elif request.reset_type == 0x02:
            logger.info("Performing hard ECU reset...")
            self.reset_ecu_simulation()
        else:
            return self.negative_response(0x11, 0x7E)
        return ECUResetResponse(response_id=0x11)

    def handle_clear_diagnostic_information(
        self, request: ClearDiagnosticInformationRequest
    ):
        if not self.is_session_allowed(request.service_id):
            return self.negative_response(request.service_id, 0x7E)
        if request.identifier == 0xFFFFFFFF:
            self.ecu.state.fault_memory.clear()
        else:
            if request.identifier in self.ecu.state.fault_memory:
                del self.ecu.state.fault_memory[request.identifier]
        return ClearDiagnosticInformationResponse(response_id=0x14)

    def handle_read_dtc_information(self, request: ReadDTCInformationRequest):
        if not self.is_session_allowed(request.service_id):
            return self.negative_response(request.service_id, 0x7E)
        dtcs = self.ecu.state.fault_memory
        return ReadDTCInformationResponse(response_id=0x19, dtc_info=dtcs)

    def handle_read_data_by_identifier(self, request: ReadDataByIdentifierRequest):
        if not self.is_session_allowed(request.service_id):
            return self.negative_response(request.service_id, 0x7E)
        identifier = request.identifier
        if identifier not in self.ecu.state.identifier_data:
            return self.negative_response(request.service_id, 0x31)
        value = self.ecu.state.identifier_data[identifier]
        return ReadDataByIdentifierResponse(
            response_id=identifier, identifier=0x22, value=value
        )

    def handle_read_memory_by_address(self, request: ReadMemoryByAddressRequest):
        if not self.is_session_allowed(request.service_id):
            return self.negative_response(request.service_id, 0x7E)
        adress = request.address
        length = request.length

        read_data = self.ecu.state.memory.read_memory(adress, length)
        if read_data is None:
            return self.negative_response(request.service_id, 0x13)
        return ReadMemoryByAddressResponse(
            response_id=0x50, address=request.address, data=read_data
        )

    def handle_write_data_by_identifier(self, request: WriteDataByIdentifierRequest):
        return WriteDataByIdentifierResponse(response_id=0x50)

    def handle_io_control_by_identifier(
        self, request: InputOutputControlByIdentifierRequest
    ):
        return InputOutputControlByIdentifierResponse(response_id=0x50)

    def handle_routine_control(self, request: RoutineControlRequest):
        return RoutineControlResponse(response_id=0x50)

    def handle_request_download(self, request: RequestDownloadRequest):
        return RequestDownloadResponse(response_id=0x50)

    def handle_request_upload(self, request: RequestUploadRequest):
        return RequestUploadResponse(response_id=0x50)

    def handle_transfer_data(self, request: TransferDataRequest):
        return TransferDataResponse(response_id=0x50)

    def handle_request_transfer_exit(self, request: RequestTransferExitRequest):
        return RequestTransferExitResponse(response_id=0x50)

    def handle_tester_present(self, request: TesterPresentRequest):
        return TesterPresentResponse(response_id=0x50)

    def handle_control_dtc_setting(self, request: ControlDTCSettingRequest):
        return ControlDTCSettingResponse(response_id=0x50)

    def negative_response(self, service_id, negative_response_code):
        """Construct a negative response for the given service ID and response code."""
        return NegativeResponse(
            service_id=service_id, response_code=negative_response_code
        )
