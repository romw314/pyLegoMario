import json
from pathlib import Path

# hex to Lego RGB codes
# code messages are always shape (hexadecimal): 08004501xx00ffff
# (where xx is the tile code)
with open(Path(__file__).parent / Path("ALL_RGB_CODES.json")) as f:
    HEX_TO_RGB_TILE = {x[2]:x[1] for x in json.load(f)}

# hex to ground colors
# color messages are always shape (hexadecimal): 08004501ffffxx00
# (where xx is the color code)
HEX_TO_COLOR_TILE = {
    0x0c: "Purple",
    0x13: "White",
    0x15: "Red",
    0x17: "Blue",
    0x18: "Yellow",
    0x1a: "Black",
    0x25: "Green",
    0x38: "Nougat Brown",
    0x42: "Cyan",
    0x6a: "Brown"}

# hex to pants codes
HEX_TO_PANTS = {        # Pins
    0x00: "None",       #000000
    0x03: "Bee",        #000011
    0x05: "Luigi",      #000101
    0x06: "Frog",       #000110
    0x0a: "Tanooki",    #001010
    0x0c: "Propeller",  #001100
    0x11: "Cat",        #010001
    0x12: "Fire",       #010010
    0x14: "Penguin",    #010100
    0x21: "Mario",      #100001
    0x22: "Builder"     #100010
}

HEX_TO_HUB_ACTIONS = {
    0x30: "Hub Will Switch Off",
    0x31: "Hub Will Disconnect"
}

HEX_TO_HUB_PROPERTIES = {
    0x01: "Advertising Name",
    0x02: "Button",
    0x03: "Firmware Ver.",
    0x04: "Hardware Ver.",
    0x05: "Signal Strength",
    0x06: "Battery Voltage",
    0x07: "Battery Type",
    0x08: "Manufacturer Name",
    0x09: "Radio Firmware Version",
    0x0A: "LEGO Wireless Protocol Version",
    0x0B: "System Type ID",
    0x0C: "H/W Network ID",
    0x0D: "Primary MAC Address",
    0x0E: "Secondary MAC Address",
    0x0F: "Hardware Network Family"
}

# BLE Connection
# https://github.com/bricklife/LEGO-Mario-Reveng
LEGO_CHARACTERISTIC_UUID = "00001624-1212-efde-1623-785feabcd123"
# Request Commmands
REQUEST_RGB_COMMAND = bytearray([
                                0x05,  # message length
                                0x00,  # unused
                                0x21,  # message type (21=Port Information Request)
                                0x01,  # port ID
                                0x00   # requested information type (0=Port Value)
                                ])
REQUEST_PANTS_COMMAND = bytearray([0x05, 0x00, 0x21, 0x02, 0x00])
REQUEST_IMU_COMMAND = bytearray([0x05, 0x00, 0x21, 0x00, 0x00])

VALID_PORT_MODES = {0:(0,1), 1:(0,1), 2:(0,), 3:(0,1,2,3), 4:(0,), 6:(0,)}

def pifs_command(port: int, mode: int, notifications: bool = True, delta_interval: int = 1):
    """Creates a PORT_INPUT_FORMAT_SETUP message according to the Lego
    Wireless Protocol: https://lego.github.io/lego-ble-wireless-protocol-docs/index.html#port-input-format-setup-single

    Args:
    port (int): The designated Port.
                Port 0: Accelerometer
                Port 1: Camera
                Port 2: Binary (Pants)
                Port 3: ??
                Port 4: ??
    mode (int): The mode to set the port to. Available modes:
        Port 0: (0,1), Port 1: (0,1), Port 2: (0), Port 3: (0,1,2,3),
        Port 4: (0,1). Also see https://github.com/bricklife/LEGO-Mario-Reveng
    notifications (bool, optional): Whether to receive updates about every new
        value of the port. Defaults to True. If False, you'll need to manually
        request port values.
    delta_interval (int, optional): The necessary change in measured data to
        trigger a change in the sent value. A higher delta interval leads to
        less accurate data, but also less data traffic via bluetooth. I
        recommend 1 for every port except Port 0, which I recommend to set
        between 1 and 5 depending on your machine. Defaults to 1.

    Returns:
        bytearray: A bytearray to be sent to Lego Mario
    """
    if port not in (0,1,2,3,4):
        raise ValueError(f"Invalid Port, expected one of (0,1,2,3,4) got {port}")
    if mode not in VALID_PORT_MODES[port]:
        raise ValueError(
            f"Invalid mode {mode} for port {port}, allowed modes for this \
            port are: {VALID_PORT_MODES[port]}.")
    # Delta Interval
    try:
        int(delta_interval)
    except (TypeError, ValueError) as e:
        raise TypeError(f"Delta Interval must be castable to int, got \
                        {type(delta_interval)} instead") from e

    return bytearray([
                    0x0A,  # Message Length
                    0x00,  # Unused
                    0x41,  # Message Type
                    port,
                    mode,
                    int(delta_interval),
                    0x00,
                    0x00,
                    0x00,
                    int(bool(notifications))  # Notifications en/disabled
                    ])

# Subscribtion Commands
SUBSCRIBE_IMU_COMMAND = pifs_command(0, 0, delta_interval=2)
SUBSCRIBE_RGB_COMMAND = pifs_command(1, 0, delta_interval=1)
SUBSCRIBE_PANTS_COMMAND = pifs_command(2, 0)

MUTE_COMMAND = bytearray([
                        0x06, # message length
                        0x00, # unused, always 0
                        0x01, # message type (01 = Hub Properties)
                        0x12, # specify hub property (12 = volume)
                        0x01, # specify operation (1 = set new value)
                        0x00  # new value (0 = mute, 100 = full volume)
                        ])
DISCONNECT_COMMAND = bytearray([
                        0x04, # message length
                        0x00, # unused, always 0
                        0x02, # message type (02 = HUB Actions)
                        0x02, # specify action (02 = disconnect)
                        ])
TURN_OFF_COMMAND = bytearray([
                        0x04, # message length
                        0x00, # unused, always 0
                        0x02, # message type (02 = HUB Actions)
                        0x01, # specify action (01 = turn off)
                        ])

BINARY_GESTURES = { # most likely wrong
                0b0000000000000001: "Bump",
                0b0000000000000010: "Gesture2",
                0b0000000000000100: "Gesture4",
                0b0000000000001000: "Gesture8",
                0b0000000000010000: "Shake",
                0b0000000000100000: "Gesture32",
                0b0000000001000000: "Gesture64",
                0b0000000010000000: "Gesture128",
                0b0000000100000000: "Turning",
                0b0000001000000000: "Fastmove",
                0b0000010000000000: "Translation",
                0b0000100000000000: "HighFallCrash",
                0b0001000000000000: "DirectionChange",
                0b0010000000000000: "Reverse",
                0b0100000000000000: "Gesture16384",
                0b1000000000000000: "Jump"
}
