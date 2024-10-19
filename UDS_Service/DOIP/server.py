import socket
import threading
import argparse


class DoIPServer:
    def __init__(self, host, port=13400):
        self.server_address = (host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket
        self.sock.bind(self.server_address)
        print(f"DoIP Server is listening on {host}:{port}")

    def start(self):
        while True:
            data, address = self.sock.recvfrom(1024)  # Buffer size
            print(f"Received message from {address}: {data.hex()}")
            self.handle_request(data, address)

    def handle_request(self, data, address):
        response = b"\x10\x01"  # Example DoIP response
        self.sock.sendto(response, address)
        print(f"Sent response to {address}: {response.hex()}")


def _parser_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-h", "--host-IP", required=True, help="IP of the host machine"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parser_args()
    server = DoIPServer(host=args.host_IP)
    server_thread = threading.Thread(target=server.start)
    server_thread.start()
