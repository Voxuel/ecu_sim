---

# DoIP Server for ECU Simulation

This project implements a **DoIP (Diagnostics over Internet Protocol)** server, capable of simulating ECU (Electronic Control Unit) diagnostics and handling various UDS (Unified Diagnostic Services) requests. The server is built to comply with the **ISO 13400** standard and supports multiple diagnostic functions such as session control, tester present, and read/write data by identifier.

## Features
- **DoIP Protocol**: Implements core DoIP functionality as per ISO 13400.
- **UDS Support**: Handles diagnostic requests such as Tester Present, Read Data by Identifier, and Session Control.
- **Virtual ECU Simulation**: Simulates an ECU that responds to diagnostic messages.
- **Asynchronous Communication**: Handles multiple connections concurrently for efficient diagnostics testing.
- **Extensible Architecture**: Easily extendable to support additional UDS services and diagnostic features.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Starting the Server](#starting-the-server)
  - [Sending Requests](#sending-requests)
- [Configuration](#configuration)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Requirements
- **Python 3.8+**
- **python-can**: For handling CAN communication
- **Scapy**: For packet manipulation and sending/receiving DoIP messages
- **Wireshark (optional)**: For monitoring DoIP traffic
- **SocketCAN** (for Linux-based systems, e.g., Raspberry Pi)

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/voxuel/doip-ecu-simulation.git
    cd doip-ecu-simulation
    ```

2. **Install Dependencies**:
    Create a virtual environment and install the required Python libraries:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

    The `requirements.txt` file includes the following key dependencies:
    - `python-can`
    - `scapy`
    - `asyncio`
    - `ruamel.yaml`

3. **Network Configuration**:
    - Ensure your development machine (or Raspberry Pi) is on the same network as the client.
    - Configure the virtual CAN interface (`vcan0`) if working with SocketCAN on Linux.

## Usage

### Starting the Server
1. **Start the DoIP Server**:
    Run the main script to start the DoIP server. By default, it listens on port `12345`.
    ```bash
    python doip_server.py
    ```

2. **Configure CAN Interface (Linux)**:
    Ensure that your `vcan0` interface is up:
    ```bash
    sudo modprobe vcan
    sudo ip link add dev vcan0 type vcan
    sudo ip link set up vcan0
    ```

3. **Monitor Traffic with Wireshark** (optional):
    - Open Wireshark on your development machine and apply a filter like `tcp.port == 12345` to capture DoIP messages.
    - Use `can` filters to capture CAN messages.

### Sending Requests
Once the server is running, you can send diagnostic requests from your client application or another machine. Below is an example of sending a UDS **Tester Present** request over DoIP using `netcat`:

```bash
echo -n -e '\x02\x10\x01' | nc <server-ip> 12345
```

For more advanced diagnostics, you can use custom scripts or clients that send UDS messages as specified in **ISO 14229**.

## Configuration
The DoIP server configuration is stored in a YAML file. You can define:
- **Diagnostic services**: Set the UDS services the server supports.
- **CAN bus configuration**: Configure CAN interfaces, arbitration IDs, etc.

Example configuration:
```yaml
uds_services:
  "0x10":
    service_name: "Diagnostic Session Control"
    handler: "handle_diagnostic_session_control"
  "0x3E":
    service_name: "Tester Present"
    handler: "handle_tester_present"
```
