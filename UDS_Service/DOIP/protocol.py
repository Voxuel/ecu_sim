from scapy.packet import Packet
from scapy.fields import ByteField
from scapy.all import sendp

class DOIP(Packet):
    fields_desc = [
        ByteField("message_type", 0),
        ByteField("service_id", 0),
        ByteField("data_length", 0),
        ByteField("data", 0),
    ]
    
    def post_build(self, p, pay):
        return p + pay
    
def send_doip_packet(dst_ip, dst_port, packet):
    sendp(packet, iface="", verbose=False)