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

import asyncio
import time
from bleak import BleakScanner, BleakClient

# BLE Connection and Event Subscription
LEGO_CHARACTERISTIC_UUID = "00001624-1212-efde-1623-785feabcd123"
SUBSCRIBE_IMU_COMMAND = bytearray([0x0A, 0x00, 0x41, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x01])
SUBSCRIBE_RGB_COMMAND = bytearray([0x0A, 0x00, 0x41, 0x01, 0x00, 0x05, 0x00, 0x00, 0x00, 0x01])

# TILE IDS
HEX_TO_COLOR_TILE = {0x13: "White", 0x15:"Red", 0x17:"Blue", 0x18:"Yellow", 0x1a:"Black", 0x25:"Green", 0x6a:"Brown", 0x0c:"Purple", 0x38:"Nougat Brown", 0x42:"Cyan"}
HEX_TO_RGB_TILE = {0xb8: "Start", 0xb7: "Flag", 0x99: "BJR", 0x29: "?-Block", 0x2e: "Cloud", 0x14: "Don't Know", 0x02: "Goomba"}

class Mario:

    def __init__(self):
        self._tileEventHooks = []
        self._accelerometerEventHooks = []
        self._doLog = True
        self._run = True

    def _signed(self, char):
        return char - 256 if char > 127 else char

    def _log(self, msg):
        if self._doLog:
            print(msg)

    def AddTileHook(self, func):
        self._tileEventHooks.append(func)

    def AddAccelerometerHook(self, func):
        self._accelerometerEventHooks.append(func)

    def _callTileHooks(self, v):
        for func in self._tileEventHooks:
            func(v)

    def _callAccelerometerHooks(self, x, y, z):
        for func in self._accelerometerEventHooks:
            func(x, y, z)

    def _handle_events(self, sender, data):
        print(data.hex())

        if data[5] == data[6] == 0xff:
            self._log("No Color or Barcode detected")
            return

        # Camera Sensor Data
        if data[0] == 8:
            # RGB code
            if data[5] == 0x0:
                self._log("%s Tile, Hex: %s" % (HEX_TO_RGB_TILE.get(data[4], "Unkown RGB Code"), data.hex()))
                self._callTileHooks(HEX_TO_RGB_TILE.get(data[4], "Unkown RGB Code"))
            elif data[5] == 0xff:
                self._log("%s Ground, Hex: %s" % (HEX_TO_COLOR_TILE.get(data[6], "Unkown Color"), data.hex()))
                self._callTileHooks(HEX_TO_COLOR_TILE.get(data[6], "Unkown Color"))

        # Accelerometer data
        elif data[0] == 7:
            x = int(self._signed(data[4]))
            y = int(self._signed(data[5]))
            z = int(self._signed(data[6]))
            self._log("X: %i Y: %i Z: %i" % (x, y, z))
            self._callAccelerometerHooks(x, y, z)

    async def Run(self):
        self._run = True
        while self._run:
            self._log("Searching for Mario...")
            devices = await BleakScanner.discover()
            for d in devices:
                if d.name:
                    if d.name.lower().startswith("lego mario"):
                        try:
                            async with BleakClient(d.address) as client:
                                await client.is_connected()
                                self._log("Mario Connected")
                                await client.start_notify(LEGO_CHARACTERISTIC_UUID, self._handle_events)
                                await asyncio.sleep(0.1)
                                await client.write_gatt_char(LEGO_CHARACTERISTIC_UUID, SUBSCRIBE_IMU_COMMAND)
                                await asyncio.sleep(0.1)
                                await client.write_gatt_char(LEGO_CHARACTERISTIC_UUID, SUBSCRIBE_RGB_COMMAND)
                                while await client.is_connected() and self._run:
                                    await asyncio.sleep(0.05)
                        except:
                            pass

    def Stop(self):
        self._run = False
