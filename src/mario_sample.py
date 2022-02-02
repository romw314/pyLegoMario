"""
SAMPLE.PY
This is a sample on how to use mario.py. It shows how to register event hook 
functions and how to let the script run as an endless loop.
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
from mario import Mario, create_and_connect_mario
def my_tile_hook(mario: Mario, t: str):
    """
    Test Function which will be called as soon as a tile is detected by Mario.
    t will contain the Name of the tile that was deteced.
    """
    pass


def my_accelerometer_hook(mario: Mario, x: int, y: int, z: int):
    """
    Test Function which will be called for every change in x, y or z accelerometer value.
    """
    pass

def my_pants_hook(mario: Mario, powerup: str):
    """Test function which will be called for every time mario changes pants.

    Args:
        powerup (str): The powerup Mario turns into
    """
    pass

async def init_marios():
    NUM_PLAYERS = 1

    # Initialize Marios
    print("Turn on Mario and press Bluetooth Button")
    marios = [await create_and_connect_mario() for player in range(NUM_PLAYERS)]
    
    # Add Hook Functions
    marios[0].AddAccelerometerHook(my_accelerometer_hook)
    marios[0].AddTileHook(my_tile_hook)
    marios[0].AddPantsHook(my_pants_hook)

    loop = asyncio.get_event_loop()
    # loop.create_task(SOME COROUTINE)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(init_marios())
    loop.run_forever()