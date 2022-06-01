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
from typing import Union, Callable

LARGE = 65
def acc_to_float(number: int) -> float:
    """Converts acceleration values from tilting Lego Mario to a sensible float -1 < x < 1 to then input into control stick.

    Args:
        number (int): Lego Mario's accelerometer's output in one direction. -255 < x <255

    Returns:
        float: float to input into VX360Gamepad.left_joystick_float.
    """
    return min(max(number/18, -1), 1)

class MarioController(Mario):
    def __init__(self, 
                doLog: bool=True, 
                accelerometerEventHooks: Union[Callable, list]=None,
                tileEventHooks: Union[Callable, list]=None, 
                pantsEventHooks: Union[Callable, list]=None, 
                logEventHooks: Union[Callable, list]=None,
                defaultVolume: Union[int, None]=None
                ) -> None:

        super().__init__(doLog, accelerometerEventHooks, tileEventHooks,
                        pantsEventHooks, logEventHooks, defaultVolume)
        self.add_accelerometer_hooks(accHandling)
        self.add_tile_hooks(rgbHandling)
        self.gamepad = vg.VX360Gamepad()
        self.y_cache=[] #  cache of length 5 to store recent y accelerations

def rgbHandling(sender: MarioController, t: str) -> None:
    """
    Test Function which will be called as soon as a tile is detected by Mario.
    t will contain the Name of the tile that was deteced.
    """
    if "Start" in t: # accept both "Start - Mario" and "Start - Luigi"
        sender.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
    else:
        sender.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
    sender.gamepad.update()

def accHandling(sender: MarioController, x: int, y: int, z: int) -> None:
    # jumping and movement handling
    if y > LARGE and not "large" in sender.y_cache:
        sender.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    # keep a down for big jump
    elif "very large" in sender.y_cache:
        sender.gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    # z (ground pound/longjump)
    elif y < -60:
        if not "large" in sender.y_cache:
            sender.gamepad.left_trigger_float(1)
    else:
        # only adjust joystick if not jumping to avoid shaky inputs
        sender.gamepad.left_joystick_float(acc_to_float(x), -acc_to_float(z))
        # reset buttons
        sender.gamepad.left_trigger_float(0)
        sender.gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    
    # b button handling
    if abs(z) > 107:
        sender.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
    else:
        sender.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)

    # input moves into sender.gamepad
    sender.gamepad.update()

    # write cache
    if abs(y) > 120:
        sender.y_cache.insert(0, "very large")
    elif abs(y) > LARGE:
        sender.y_cache.insert(0, "large")
    else:
        sender.y_cache.insert(0, "small")
    sender.y_cache = sender.y_cache[:5]


if __name__ == "__main__":
    # Initialize Marios
    print("Turn on Mario and press Bluetooth Button")
    controller = MarioController(False, defaultVolume=0)
    
    #MarioWindow(controller)
    run()