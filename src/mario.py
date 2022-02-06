"""
MARIO.PY
This is a little script that connects to Lego Mario and then reads its
acceleromter and tile sensor data. It does so until you call Stop() and turn of 
Mario. It also automatically reconnects to MArio if it it looses the connection.
To connect you have to turn Mario on and then press the Bluetooth Button.
See sample.py on how to use it.
###################################################################################
MIT License
Copyright (c) 2020 Bruno Hautzenberger
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# only needed if you use scripts both in src and in parent directories
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parents[1]))
from src.LEGO_MARIO_DATA import *
# if you only use scripts inside src, instead use
# from LEGO_MARIO_DATA import *
# if you only access mario from parent directories, use
# from .LEGO_MARIO_DATA import *

import asyncio, aioconsole
from bleak import BleakScanner, BleakClient, BleakError
from typing import Callable, Union


class Mario:

    def __init__(self, doLog=True, accelerometerEventHooks=None, tileEventHooks=None, pantsEventHooks=None):
        self._accelerometerEventHooks = []
        self._tileEventHooks = []
        self._pantsEventHooks = []
        self._doLog = doLog
        self._run = True
        self._client = None
        self.AddAccelerometerHook(accelerometerEventHooks)
        self.AddTileHook(tileEventHooks)
        self.AddPantsHook(pantsEventHooks)

    def _signed(self, char):
        return char - 256 if char > 127 else char

    def _log(self, msg, end="\n"):
        """Log any message to stdout. Will also include mario's address.

        Args:
            msg (object): Any printable object.
            end (str, optional): Same as end in print(). Defaults to "\n".
        """
        if self._doLog:
            address = "Not Connected" if not self._client else self._client.address
            print(("\r%s: %s" % (address, msg)).ljust(70), end=end)

    def AddTileHook(self, funcs: Union[Callable, list]) -> None:
        """Adds function(s) as event hooks for updated tile or color values.

        Args:
            funcs (function or list of functions): function or list of functions that take (Mario, str) as input.
        """
        if hasattr(funcs, '__iter__'):
            for function in funcs:
                if callable(function):
                    self._tileEventHooks.append(function)
        elif callable(funcs):
            self._tileEventHooks.append(funcs)

    def AddAccelerometerHook(self, funcs: Union[Callable, list]) -> None:
        """Adds function(s) as event hooks for updated accelerometer values.

        Args:
            funcs (function or list of functions): function or list of functions that take (Mario, int, int, int) as input.
        """
        if hasattr(funcs, '__iter__'):
            for function in funcs:
                if callable(function):
                    self._accelerometerEventHooks.append(function)
        elif callable(funcs):
            self._accelerometerEventHooks.append(funcs)

    def AddPantsHook(self, funcs: Union[Callable, list]) -> None:
        """Adds function(s) as event hooks for updated pants values.

        Args:
            funcs (function or list of functions): function or list of functions that take a Mario object and a single string as input.
        """
        if hasattr(funcs, '__iter__'):
            for function in funcs:
                if callable(function):
                    self._pantsEventHooks.append(function)
        elif callable(funcs):
            self._pantsEventHooks.append(funcs)

    def _callTileHooks(self, tile: str) -> None:
        for func in self._tileEventHooks:
            func(self, tile)

    def _callAccelerometerHooks(self, x: int, y: int, z: int) -> None:
        for func in self._accelerometerEventHooks:
            func(self, x, y, z)
    
    def _callPantsHooks(self, powerup: str) -> None:
        for func in self._pantsEventHooks:
            func(self, powerup)

    def _handle_events(self, sender, data: bytearray) -> None:
        hex_data = data.hex()
        # Port Value
        if data[2] == 0x45:
            # Camera Sensor Data
            if data[3] == 0x01:
                if data[5] == data[6] == 0xff:
                    self._log("IDLE? %s" % hex_data)
                    return
                # RGB code
                if data[5] == 0x0:
                    self._log("%s Tile, Hex: %s" % (HEX_TO_RGB_TILE.get(data[4], "Unkown RGB Code"), hex_data))
                    self._callTileHooks(HEX_TO_RGB_TILE.get(data[4], "Unkown RGB Code: %s" % hex_data))
                # Ground Colors
                elif data[5] == 0xff:
                    self._log("%s Ground, Hex: %s" % (HEX_TO_COLOR_TILE.get(data[6], "Unkown Color"), hex_data))
                    self._callTileHooks(HEX_TO_COLOR_TILE.get(data[6], "Unkown Color: %s" % hex_data))

            # Accelerometer data
            elif data[3] == 0x00:
                # Gesture Mode
                if data[4:6] == data[6:]:
                    gesture = ""
                    integer_data = int.from_bytes(data[4:6], "big")
                    for bin_gest in BINARY_GESTURES.keys():
                        if integer_data & bin_gest:
                            gesture += BINARY_GESTURES[bin_gest]
                    self._log(gesture)

                # RAW Mode
                else:
                    x = int(self._signed(data[4]))
                    y = int(self._signed(data[5]))
                    z = int(self._signed(data[6]))
                    self._log("X: %i Y: %i Z: %i" % (x, y, z), end="")
                    self._callAccelerometerHooks(x, y, z)

            # Pants data
            elif data[3] == 0x02:
                pants = HEX_TO_PANTS.get(data[4], "Unkown")
                binary_pants = bin(data[4])
                self._log("%s Pants, Hex: %s, Pants-Only Binary: %s" % (pants, hex_data, binary_pants))
                self._callPantsHooks(pants)
            else:
                self._log("Unknown port value - check the Lego Wireless Protocol for the following - Hex: %s" % hex_data)

        # other technical messages
        elif data[2] == 0x02: # Hub Actions
            self._log("%s, Hex: %s" % (HEX_TO_HUB_ACTIONS.get(data[3], "Unkown Hub Action, Hex: %s" % hex_data), hex_data))
            if data[3] == 0x31: # 0x31 = Hub Will Disconnect
                asyncio.get_event_loop().create_task(self.disconnect())
        elif data[2] == 0x04: # Hub Attached I/O
            self._log("Port %s got %s, Hex: %s" % (data[3], "attached" if data[4] else "detached - this shouldn't happen with Mario", hex_data))
        elif data[2] == 0x47: # Port Input Format Handshake
            self._log("Port %s got changed into mode %s with notifications %s" % (data[3], data[4], "Enabled" if data[9] else "Disabled"))
        else:   # Other
            self._log("Unknown message - check the Lego Wireless Protocol for the following - Hex: %s" % hex_data)

    async def connect(self):
        self._run = True
        while self._run:
            self._log("Searching for device...")
            devices = await BleakScanner.discover()
            for d in devices:
                if d.name and (d.name.lower().startswith("lego luigi") or d.name.lower().startswith("lego mario")):
                    try:
                        client = BleakClient(d.address)
                        await client.connect()
                        self._client = client
                        self._log("Mario Connected: %s" % client.address)
                        await client.start_notify(LEGO_CHARACTERISTIC_UUID, self._handle_events)
                        await asyncio.sleep(0.1)
                        await client.write_gatt_char(LEGO_CHARACTERISTIC_UUID, SUBSCRIBE_IMU_COMMAND)
                        await asyncio.sleep(0.1)
                        await client.write_gatt_char(LEGO_CHARACTERISTIC_UUID, SUBSCRIBE_RGB_COMMAND)
                        await asyncio.sleep(0.1)
                        await client.write_gatt_char(LEGO_CHARACTERISTIC_UUID, SUBSCRIBE_PANTS_COMMAND)
                        client.is_connected
                        return True
                    except: # any error during communication
                        self._log("Error connecting")
                        await self.disconnect()
                        return False

    async def request_port_value(self, port:int=0) -> None:
        """Method for sending request for color sensor port value to Mario.
        Default port is 0.
        0 - Accelerometer
        1 - Camera
        2 - Pants
        3 - unknown
        4 - unknown
        6 - voltage?
        Response will be sent to event handlers.

        Args:
            port (int, optional): Port to request value from. Defaults to 0.
        """
        assert port in (0,1,2,3,4, 6), "Use a supported port (0,1,2,3,4,6)"
        if self._client:
            try:
                await self._client.write_gatt_char(LEGO_CHARACTERISTIC_UUID, bytearray([*REQUEST_RGB_COMMAND[:3], port, *REQUEST_RGB_COMMAND[4:]]))
            except (OSError, BleakError):
                self._log("Connection error while requesting port value")
                await self.disconnect()

    async def set_volume(self, new_volume: int) -> None:
        """Sets mario's volume to the specified volume.

        Args:
            new_volume (int): Percentage of maximum volume. Values <0 or >100 will be set to 0 or 100 respectively.
        """
        new_volume = min(max(new_volume, 0), 100)
        if self._client:
            try:
                await self._client.write_gatt_char(LEGO_CHARACTERISTIC_UUID, bytearray([*MUTE_COMMAND[:5], new_volume]))
            except (OSError, BleakError):
                self._log("Connection error while setting volume")
                await self.disconnect()

    async def check_connection_loop(self) -> None:
        while self._client:
            try:
                if not self._client.is_connected:
                    self._log("Disconnect detected during connection check")
                    await self.disconnect()
                await asyncio.sleep(3)
            except (OSError, BleakError):
                self._log("Error during connection check")
                await self.disconnect()

    async def disconnect(self) -> None:
        try:
            self._log("Disconnecting... ")
            if self._client:
                await self._client.write_gatt_char(LEGO_CHARACTERISTIC_UUID, DISCONNECT_COMMAND)
                await self._client.disconnect()
                self._client = None
            self._run = False
        except (OSError, BleakError):
            self._log("Connection error while disconnecting")
            self._client = None
            self._run = False
        
        reconnect = await aioconsole.ainput("Reconnect? (Y/N)")
        if reconnect.lower().startswith("y"):
            await self.connect()

    async def turn_off(self) -> None:
        try:
            self._log("Turning Off... ")
            await self._client.write_gatt_char(LEGO_CHARACTERISTIC_UUID, TURN_OFF_COMMAND)
            await self.disconnect()
        except (OSError, BleakError):
                self._log("Connection error while turning off")
                await self.disconnect()

async def create_and_connect_mario(doLog=True, accelerometerEventHooks=None, tileEventHooks=None, pantsEventHooks=None) -> Mario:
    new_mario = Mario(**locals()) # **locals() passes the keyword arguments from above
    await new_mario.connect()
    loop = asyncio.get_event_loop()
    loop.create_task(new_mario.check_connection_loop())
    return new_mario