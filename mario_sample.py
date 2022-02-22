"""
SAMPLE.PY
This is a sample on how to use mario.py. It shows how to register event hook 
functions and how to let the script run as an endless loop.
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

import asyncio
from pyLegoMario import Mario, MarioWindow, run

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


if __name__ == "__main__":
    NUM_PLAYERS = 1
    # Initialize Marios
    marios = [Mario(doLog = True, accelerometerEventHooks = my_accelerometer_hook, tileEventHooks = my_tile_hook) for player in range(NUM_PLAYERS)]
    """Add Event Hooks in constructor (above) or manually (below).
    Event hooks are functions that are called every time Mario sends data of a certain kind.
    The functions in this example don't do anything. Try inserting a print call."""
    # create GUI windows
    for mario in marios:
        MarioWindow(mario)
    marios[0].AddPantsHook(my_pants_hook)
    # Change Mario's Volume (0-100)
    marios[0].set_volume(40)
    # loop.create_task(SOME COROUTINE)
    
    run()