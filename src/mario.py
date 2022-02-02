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

import asyncio
from bleak import BleakScanner, BleakClient


class Mario:

    def __init__(self, doLog=True):
        self._tileEventHooks = []
        self._accelerometerEventHooks = []
        self._pantsEventHooks = []
        self._doLog = doLog
        self._run = True
        self._client = None

    def _signed(self, char):
        return char - 256 if char > 127 else char

    def _log(self, msg, end="\n"):
        if self._doLog:
            print(("\r%s: %s" % ("Not Connected" if not self._client else self._client.address, msg)).ljust(70), end=end)

    def AddTileHook(self, func):
        self._tileEventHooks.append(func)

    def AddAccelerometerHook(self, func):
        self._accelerometerEventHooks.append(func)

    def AddPantsHook(self, func):
        self._pantsEventHooks.append(func)

    def _callTileHooks(self, tile: str):
        for func in self._tileEventHooks:
            func(self, tile)

    def _callAccelerometerHooks(self, x, y, z):
        for func in self._accelerometerEventHooks:
            func(self, x, y, z)
    
    def _callPantsHooks(self, powerup: str):
        for func in self._pantsEventHooks:
            func(self, powerup)

    def _handle_events(self, sender, data: bytearray):
        # Camera Sensor Data
        if data[0] == 0x8:
            if data[5] == data[6] == 0xff:
                self._log("No Color or Barcode detected: %s" % data.hex())
                return
            # RGB code
            if data[5] == 0x0:
                self._log("%s Tile, Hex: %s" % (HEX_TO_RGB_TILE.get(data[4], "Unkown RGB Code"), data.hex()))
                self._callTileHooks(HEX_TO_RGB_TILE.get(data[4], "Unkown RGB Code: %s" % data.hex()))
            # Ground Colors
            elif data[5] == 0xff:
                self._log("%s Ground, Hex: %s" % (HEX_TO_COLOR_TILE.get(data[6], "Unkown Color"), data.hex()))
                self._callTileHooks(HEX_TO_COLOR_TILE.get(data[6], "Unkown Color: %s" % data.hex()))

        # Accelerometer data
        elif data[0] == 0x7:
            x = int(self._signed(data[4]))
            y = int(self._signed(data[5]))
            z = int(self._signed(data[6]))
            self._log("X: %i Y: %i Z: %i" % (x, y, z), end="")
            self._callAccelerometerHooks(x, y, z)

        # Pants data
        elif data[0] == 0x5:
            self._log("%s Pants, Hex: %s" % (HEX_TO_PANTS.get(data[4], "Unkown Powerup"), data.hex()))
            self._callPantsHooks(HEX_TO_PANTS.get(data[4], "Unkown Powerup: Binary; %s, Hex: %s" % (bin(data[4]), data.hex())))

    async def connect(self):
        self._run = True
        while self._run:
            self._log("Searching for Mario...")
            devices = await BleakScanner.discover()
            for d in devices:
                if d.name and d.name.lower().startswith("lego mario"):
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
        3 - TBD
        4 - TBD
        Response will be sent to event handlers.

        Args:
            port (int, optional): Port to request value from. Defaults to 0.
        """
        assert port in (0,1,2,3,4), "Only use ports 0-4"
        if self._client:
            try:
                await self._client.write_gatt_char(LEGO_CHARACTERISTIC_UUID, [*REQUEST_RGB_COMMAND[:3], port, *REQUEST_RGB_COMMAND[4:]])
            except OSError:
                self._log("Connection error while requesting port value")
                await self.disconnect()

    async def check_connection_loop(self):
        while self._client:
            try:
                if not self._client.is_connected:
                    self._log("Disconnect detected")
                    await self.disconnect()
                    return
                await asyncio.sleep(3)
            except OSError:
                self._log("Error during connection check")
                await self.disconnect()

    async def disconnect(self):
        try:
            self._log("Disconnecting... ")
            if self._client:
                await self._client.disconnect()
                self._client = None
            self._run = False
        except OSError:
            self._log("Connection error while disconnecting")
            self._client = None
            self._run = False

async def create_and_connect_mario(doLog=True):
    new_mario = Mario(doLog=doLog)
    await new_mario.connect()
    loop = asyncio.get_event_loop()
    loop.create_task(new_mario.check_connection_loop())
    return new_mario