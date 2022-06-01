"""
mairo_soundboard.py
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

import json, os, asyncio, random, sys
from typing import Callable, Union
from pyLegoMario import Mario, MarioWindow, run
from pathlib import Path
import soundfile as sf
import sounddevice as sd
from pyLegoMario.LEGO_MARIO_DATA import HEX_TO_RGB_TILE
import pyinputplus as pyip


async def register_sounds(
    mario: Mario, 
    sounds: dict[str, list[sf.SoundFile]]
    ) -> dict[str, str]:
    """Use Lego Mario to have the user assign RGB tiles to sounds.

    Args:
        mario (Mario): Instance of Lego Mario that's used for scanning.
        sounds (dict[str, list[sf.SoundFile]]): Dictionary of file or directory names assigned to lists of sound files.

    Returns:
        dict[str, str]: A mapping of tile names to sound file or directory names.
    """
    settings = load_settings()
    saved_mappings = settings.get("sound_mappings", {})
    
    tile_mapping = {} # tile_name : sound_name
    for tile_name, sound_name in saved_mappings.items():
        # copy old settings
        if sound_name in sounds.keys():
            tile_mapping[tile_name] = sound_name
            mario.log(f"Imported {tile_name}: {sound_name}")
        else:
            # drop invalid setting by saving copy without that mapping
            mario.log(f"Invalid setting: file {sound_name} not found. Setting deleted.")

    for sound_name, sound_list in sounds.items():
        # check if already registered from settings
        if not sound_name in tile_mapping.values():
            display_name = (f"sound{' group' if len(sound_list) > 1 else ''}:"
                            f" {sound_name}")
            mario.log(
                f"Please scan tile for this {display_name}")
            # unpack needed because sound contains data & bitrate
            sd.play(*random.choice(sound_list), device=device)
            # Add event hook that registers sound
            def register_sound_id(sender: Mario, t: str):
                # only tiles & no already registered tiles
                if t in tile_mapping.keys():
                    sender.log(
                        f"{t} is already registered to {tile_mapping[t]}")
                elif t in HEX_TO_RGB_TILE.values():
                    tile_mapping[t] = sound_name
                    # remove event hook as soon as tile was registered
                    sender.remove_hooks(register_sound_id)
                    mario.log(f"Registered {display_name} to tile {t}")
            mario.add_tile_hooks(register_sound_id)
            # wait for registration
            while not sound_name in tile_mapping.values():
                await asyncio.sleep(0.5)
            # save after each new registration
            settings["sound_mappings"] = tile_mapping
            save_settings(settings)
    return tile_mapping

def select_audio_device(mario: Mario) -> int:
    """Prompts the user to to select one of their available audio devices.

    Args:
        mario (Mario): Only for logging.

    Returns:
        int: Selected audio device.
    """
    available_devices = sd.query_devices()
    try:
        mario.log("Check console to select audio device")
    except:
        pass
    prompt = (f"{str(available_devices)}\n"
            "Please choose one of the output devices by entering a number.")
    return pyip.inputInt(prompt, min=0, max=len(available_devices) - 1)

def load_settings() -> dict[str, Union[int, str]]:
    try:
        with open(DIR_PATH / "settings.json", "r") as f:
            settings = json.load(f)
    except FileNotFoundError:
        mario.log("No previous settings found, starting from scratch.")
        settings = {}
    except json.JSONDecodeError:
        mario.log("Invalid JSON file. Loading empty settings.")
        settings = {}
    return settings

def save_settings(settings: dict) -> None:
    mario.log("Saving settings")
    with open(DIR_PATH / "settings.json", "w") as f:
            json.dump(settings, f, indent=4)

def get_sounds(folder_path: Union[str, Path]) -> dict[str, list[sf.SoundFile]]:
    sounds = {}
    for name in os.listdir(folder_path):
        if name.endswith(".wav"):
            sounds[name] = [sf.read(folder_path / name)]
        # if directory, register all WAV sounds inside
        elif os.path.isdir(folder_path / name):
            sounds[name] = [
                sf.read(folder_path / name / file_name)
                for file_name in os.listdir(folder_path / name)
                if file_name.endswith(".wav")
            ]
    return sounds

def tile_hook_factory(
    sound_mapping: dict[str, str],
    sounds: dict[str, list[sf.SoundFile]],
    device: int
    ) -> Callable[[Mario, str], None]:
    """Generates a function that can be registered as Mario's rgb event hook.

    Args:
        sound_mapping (dict[str, str]): A mapping from tiles to sound names.
        sounds (dict[str, list[sf.SoundFile]]): Mapping of sound names to
            SoundFile data.
        device (int): The device that should be used to play back the sounds.

    Returns:
        Callable: function that can be registered as tile event hook for mario.
    """
    def play_tile_sound(sender: Mario, tile: str) -> None:
        # check for mapped sound
        if tile in sound_mapping.keys():
            # play mapped sound
            sd.play(*random.choice(sounds[sound_mapping[tile]]), device=device)
            sender.log(f"Playing sound {sound_mapping[tile]}")
    return play_tile_sound

if __name__ == "__main__":
    DIR_PATH = Path(sys.argv[0]).parent / "mario_soundboard_files"
    if not os.path.isdir(DIR_PATH):
        os.mkdir(DIR_PATH)
    # Initialize Mario
    mario = Mario(True, default_volume=0)
    MarioWindow(mario)
    
    settings = load_settings()
    try:
        device = settings["device"]
    except KeyError:
        device = select_audio_device(mario)
        settings["device"] = device
        save_settings(settings)

    sounds = get_sounds(DIR_PATH)
    loop = asyncio.get_event_loop()
    sound_mapping = loop.run_until_complete(register_sounds(mario, sounds))
    play_sound_tile_hook = tile_hook_factory(sound_mapping, sounds, device)
    mario.add_tile_hooks(play_sound_tile_hook)
    run()