from UDS_Service.models.ECU import ECU

class UDSHandler:
    def __init__(self, config, ecu: ECU):
        self.config = config
        self.ecu = ecu

    def handle_request(self, data: bytearray):
        service_id = data[0]

        if service_id == 0x10:  
            return self.handle_session_control(data)
        elif service_id == 0x22:  
            return self.handle_read_data_by_identifier(data)
        elif service_id == 0x3E:  
            return self.handle_tester_present(data)
        else:
            return self.negative_response(service_id, 0x12)  

    def handle_session_control(self, data: bytearray):
        sub_function = data[1]
        self.ecu.state.session_active = True
        self.ecu.state.active_session = sub_function
        return b"\x03\x50" + bytes([sub_function])

    def handle_tester_present(self, data: bytearray):
        if self.ecu.state.session_active:
            return b"\x02\x7e\x3e"  
        else:
            return self.negative_response(0x3E, 0x7F)  

    def handle_read_data_by_identifier(self, data: bytearray):
        if len(data) < 4:
            return self.negative_response(service_id=0x22, error_code=0x13)
        identifier = (data[1] << 8) | data[2]
        if identifier == 0xF190:
            vin_data = self.ecu.get_data_by_identifier(0xF190)
            return b"\x10" + vin_data
        elif identifier == 0xF186:
            current_session = self.ecu.get_active_session()
            response_data = bytearray([0x62, 0xF1, 0x86]) + current_session
            return response_data
        else:
            return self.negative_response(0x22, 0x11)  

    def negative_response(self, service_id: int, error_code: int):
        return b"\x03\x7f" + bytes([service_id]) + bytes([error_code])
