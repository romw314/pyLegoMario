"""
MARIO.PY
###################################################################################
MIT License
Copyright (c) 2022 Bruno Hautzenberger, Jamin Kauf
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
from .LEGO_MARIO_DATA import *
# if you only use scripts inside src, instead use
# from LEGO_MARIO_DATA import *
# if you only access mario from parent directories, use
# from .LEGO_MARIO_DATA import *

import asyncio
from bleak import BleakScanner, BleakClient, BleakError
from typing import Callable, Union


class Mario:

    def __init__(self, doLog: bool=True, accelerometerEventHooks: Union[Callable, list]=None, tileEventHooks: Union[Callable, list]=None, pantsEventHooks: Union[Callable, list]=None, logEventHooks: Union[Callable, list]=None):

        self._doLog = doLog
        self._run = False
        self._autoReconnect = True
        self._client = None

        # values to keep most recent event in memory
        self.pants = None
        self.ground = None
        self.acceleration = None
        self.recentTile = None

        self._accelerometerEventHooks = []
        self._tileEventHooks = []
        self._pantsEventHooks = []
        self._logEventHooks = []

        self.AddAccelerometerHook(accelerometerEventHooks)
        self.AddTileHook(tileEventHooks)
        self.AddPantsHook(pantsEventHooks)
        self.AddLogHook(logEventHooks)

        self.ALLHOOKS = (self._accelerometerEventHooks, self._pantsEventHooks, self._tileEventHooks, self._logEventHooks)

        try: # if event loop exists, use that one
            asyncio.get_event_loop().create_task(self.connect())
        except RuntimeError: # otherwise, create a new one
            asyncio.set_event_loop(asyncio.SelectorEventLoop())
            asyncio.get_event_loop().create_task(self.connect())

    def _signed(self, char):
        return char - 256 if char > 127 else char

    def _log(self, msg, end="\n"):
        """Log any message to stdout and call all assigned LogEvent handlers.

        Args:
            msg (object): Any printable object.
            end (str, optional): Same as end in print(). Defaults to "\n".
        """
        for func in self._logEventHooks:
            func(self, msg)
        if self._doLog:
            address = "Not Connected" if not self._client else self._client.address
            print(("\r%s: %s" % (address, msg)).ljust(100), end=end)

    def AddLogHook(self, funcs: Union[Callable, list]) -> None:
        """Adds function(s) as event hooks for updated tile or color values.

        Args:
            funcs (function or list of functions): function or list of functions that take (Mario, str) as input.
        """
        if hasattr(funcs, '__iter__'):
            for function in funcs:
                if callable(function):
                    self._logEventHooks.append(function)
        elif callable(funcs):
            self._logEventHooks.append(funcs)

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
        
    def RemoveEventsHook(self, funcs: Union[Callable, list]) -> None:
        """Removes function(s) as event hooks, no matter what kind of hook they were.

        Args:
            funcs (function or list of functions): function or list of functions.
        """
        
        if hasattr(funcs, '__iter__'):
            for hooktype in self.ALLHOOKS:
                for function in funcs:
                    if callable(function) and function in hooktype:
                        hooktype.remove(function)
        elif callable(funcs):
            for hooktype in self.ALLHOOKS:
                if funcs in hooktype:
                    hooktype.remove(funcs)

    def _callTileHooks(self, tile: str) -> None:
        self.ground = tile
        for func in self._tileEventHooks:
            func(self, tile)

    def _callAccelerometerHooks(self, x: int, y: int, z: int) -> None:
        self.acceleration = (x, y, z)
        for func in self._accelerometerEventHooks:
            func(self, x, y, z)
    
    def _callPantsHooks(self, powerup: str) -> None:
        self.pants = powerup
        for func in self._pantsEventHooks:
            func(self, powerup)

    def _handle_events(self, sender, data: bytearray) -> None:
        hex_data = data.hex()
        # Port Value
        if data[2] == 0x45:
            # Camera Sensor Data
            if data[3] == 0x01:
                if data[5] == data[6] == 0xff:
                    self._log("IDLE?, Hex: %s" % hex_data)
                    return
                # RGB code
                if data[5] == 0x00:
                    tile = HEX_TO_RGB_TILE.get(data[4], "Unkown Tile Code") # decode tile
                    self.recentTile = tile
                    self._log("%s Tile, Hex: %s" % (tile, hex_data))
                    self._callTileHooks(tile)
                # Ground Colors
                elif data[5] == 0xff:
                    color = HEX_TO_COLOR_TILE.get(data[6], "Unkown Color")
                    self._log("%s Ground, Hex: %s" % (color, hex_data))
                    self._callTileHooks(color)

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
                self._log("%s Pants, Pants-Only Binary: %s, Hex: %s" % (pants, binary_pants, hex_data))
                self._callPantsHooks(pants)
            # Port 3 data - uncertain about all of it
            elif data[3] == 0x03:
                if data[4] == 0x13 and data[5] == 0x01:
                    tile = HEX_TO_RGB_TILE.get(data[6], "Unkown Tile")
                    self._log("Port 3: Jumped on %s, Hex: %s" % (tile, hex_data))
                else:
                    #TBD
                    self._log("Unknown value from port 3: %s, Hex: %s" % (data[4:].hex(), hex_data))
            else:
                self._log("Unknown value from port %s: %s, Hex: %s" % (data[3], data[4:].hex(), hex_data))

        # other technical messages
        elif data[2] == 0x02: # Hub Actions
            self._log("%s, Hex: %s" % (HEX_TO_HUB_ACTIONS.get(data[3], "Unkown Hub Action, Hex: %s" % hex_data), hex_data))
            if data[3] == 0x31: # 0x31 = Hub Will Disconnect
                asyncio.get_event_loop().create_task(self.disconnect())
        elif data[2] == 0x04: # Hub Attached I/O
            self._log("Port %s got %s, Hex: %s" % (data[3], "attached" if data[4] else "detached - this shouldn't happen with Mario", hex_data))
        elif data[2] == 0x47: # Port Input Format Handshake
            self._log("Port %s changed to mode %s %s notifications, Hex: %s" % (data[3], data[4], "with" if data[9] else "without", hex_data))
        elif data[2] == 0x01 and data[4] == 0x06:
            property = HEX_TO_HUB_PROPERTIES.get(data[3], "Unknown Property")
            self._log("Hub Update About %s: %s, Hex: %s" % (property, data[5:].hex(), hex_data))
        else:   # Other
            self._log("Unknown message - check Lego Wireless Protocol, Hex: %s" % hex_data)

    async def connect(self):
        self._run = True
        retries=0
        while self._run:
            retries+=1
            if retries > 3:
                self._log("Stopped after 3 attempts, disconnecting...")
                break
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
                        asyncio.get_event_loop().create_task(self.check_connection_loop())
                        return True
                    except: # any error during communication
                        self._log("Error connecting")
                        await self.disconnect()
                        return False
        await self.disconnect()

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
        assert port in (0,1,2,3,4,6), "Use a supported port (0,1,2,3,4,6)"
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
        except (OSError, BleakError):
            self._log("Connection error while disconnecting")
            self._client = None
        if self._autoReconnect:
            await self.connect()
        else:
            self._run = False

    async def turn_off(self) -> None:
        try:
            self._log("Turning Off... ")
            await self._client.write_gatt_char(LEGO_CHARACTERISTIC_UUID, TURN_OFF_COMMAND)
            await self.disconnect()
        except (OSError, BleakError):
                self._log("Connection error while turning off")
                await self.disconnect()

def run():
    while asyncio.all_tasks(loop=asyncio.get_event_loop()):
        asyncio.get_event_loop().run_until_complete(asyncio.gather(*asyncio.all_tasks(loop=asyncio.get_event_loop())))