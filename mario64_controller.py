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
import vgamepad as vg
from pyLegoMario import *


def my_tile_hook(mario: Mario, t: str):
    """
    Test Function which will be called as soon as a tile is detected by Mario.
    t will contain the Name of the tile that was deteced.
    """
    if t == "Baby Penguin":
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
        
    else:
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
    gamepad.update()

def acc_to_float(number: int) -> float:
    return min(max(number/22, -1), 1)

LARGE = 65
def my_accelerometer_hook(mario: Mario, x: int, y: int, z: int):
    """
    Test Function which will be called for every change in x, y or z accelerometer value.
    """
    # jumping and movement handling
    if y > LARGE and not "large" in mario.y_cache:
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    # keep a down for big jump
    elif "very large" in mario.y_cache:
        gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        # z (ground pound/longjump)
    elif y < -60:
        if not "large" in mario.y_cache:
            gamepad.left_trigger_float(1)
    else:
        # only adjust joystick if not jumping to avoid shaky inputs
        gamepad.left_joystick_float(acc_to_float(x), -acc_to_float(z))
        # reset buttons
        gamepad.left_trigger_float(0)
        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    
    # b button handling
    if abs(z) > 100:
        gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
    else:
        gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)

    # input moves into gamepad
    gamepad.update()

    # write cache
    if abs(y) > 120:
        mario.y_cache.insert(0, "very large")
    elif abs(y) > LARGE:
        mario.y_cache.insert(0, "large")
    else:
        mario.y_cache.insert(0, "small")
    mario.y_cache = mario.y_cache[:5]

def my_pants_hook(mario: Mario, powerup: str):
    """Test function which will be called for every time mario changes pants.

    Args:
        powerup (str): The powerup Mario turns into
    """
    pass


if __name__ == "__main__":
    gamepad = vg.VX360Gamepad()
    # Initialize Marios
    print("Turn on Mario and press Bluetooth Button")
    mario = Mario(True, my_accelerometer_hook, my_tile_hook, my_pants_hook, defaultVolume=0)
    mario.y_cache=[]
    MarioWindow(mario)
    run()