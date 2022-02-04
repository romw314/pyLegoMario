# hex to ground colors
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

# hex to Lego RGB codes
HEX_TO_RGB_TILE = {             # Dec | Same Codes
    0x02: 'Goomba',             #   2 | Fly Guy, Foo, Ant Trooper, Ninji, Para-Goomba, Goombrat, Bone Goomba
    0x0b: 'Lego NES',           #  11 |
    0x0d: 'Thwimp',             #  13 |
    0x0e: 'Bob-omb',            #  14 |
    0x14: 'Rotation',           #  20 |
    0x9f: 'Pink Yoshi',         #  25 |
    0x23: 'Poison Mushroom',    #  35 |
    0x29: '?-Block',            #  41 |
    0x2e: 'Cloud',              #  46 |
    0x30: 'Beetle',             #  48 | Para-Beetle, Mechakoopa
    0x60: 'Boom Boom',          #  96 |
    0x6a: "Peach's Castle",     # 106 |
    0x81: 'Peeper',             # 129 |
    0x89: 'Urchin',             # 137 | Spiny Cheep Cheep
    0x91: 'Wrench',             # 145 |
    0x99: 'BJR',                # 153 |
    0xa0: "Gear",               # 160 |
    0xab: 'Seesaw',             # 171 |
    0xae: 'Boo',                # 174 |
    0xb7: 'Flag',               # 183 |
    0xb8: 'Start - Mario',      # 184 |
    0xaf: 'Start - Luigi',      # 176 |
    0xf4: 'Coin Coffer'}        # 244 |

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

# BLE Connection
# https://github.com/bricklife/LEGO-Mario-Reveng
LEGO_CHARACTERISTIC_UUID = "00001624-1212-efde-1623-785feabcd123"
# Request Commmands
REQUEST_RGB_COMMAND = bytearray([
                                0x05, # message length
                                0x00, # unused
                                0x21, # message type (21=Port Information Request)
                                0x01, # port ID
                                0x00  # requested information type (0=Port Value)
                                ])
REQUEST_PANTS_COMMAND = bytearray([0x05, 0x00, 0x21, 0x02, 0x00])
REQUEST_IMU_COMMAND = bytearray([0x05, 0x00, 0x21, 0x00, 0x00])
# Subscribtion Commands
SUBSCRIBE_IMU_COMMAND =  bytearray([0x0A, # Length of message
                                    0x00, # unused, always 0
                                    0x41, # message type (41=Port Input Format Setup)
                                    0x00, # port ID (0=accelerometer)
                                    0x00, # mode (0=RAW)
                                    0x04, # delta interval
                                    0x00, # delta interval
                                    0x00, # delta interval
                                    0x00, # delta interval
                                    0x01] # Enable Notifications (1=y, 0=n)
                                    )
SUBSCRIBE_RGB_COMMAND =  bytearray([0x0A,
                                    0x00,
                                    0x41,
                                    0x01, # port ID 1=tile scanner
                                    0x00,
                                    0x05,
                                    0x00,
                                    0x00,
                                    0x00,
                                    0x01])
SUBSCRIBE_PANTS_COMMAND = bytearray([0x0A,
                                    0x00, 
                                    0x41, 
                                    0x02, # port ID 2=pants sensor
                                    0x00, 
                                    0x05, 
                                    0x00, 
                                    0x00, 
                                    0x00, 
                                    0x01])
MUTE_COMMAND = bytearray([
                        0x06, # message length
                        0x00, # unused, always 0
                        0x01, # message type (01 = Hub Properties)
                        0x12, # specify hub property (12 = volume)
                        0x01, # specify operation (1 = set new value)
                        0x00  # new value (0 = mute, 100 = full volume)
                        ])