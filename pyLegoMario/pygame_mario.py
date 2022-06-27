"""
pygame_mario.py
This file implements class PygameMario that subclasses Mario to utilize pygame
events. It also implements AsyncClock, which behaves like a regular pygame
clock but also keeps Mario running.
Copyright (c) 2022 Jamin Kauf
"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame.locals import *
try:
    from mario import Mario
except ImportError:
    from .mario import Mario
import asyncio

ACC_EVENT = pygame.event.custom_type()
RGB_EVENT = pygame.event.custom_type()
PANTS_EVENT = pygame.event.custom_type()

def _acceleration_callback(mario: Mario, x: int, y: int, z: int):
    event = pygame.event.Event(ACC_EVENT, value=(x,y,z), sender=mario)
    pygame.event.post(event)

def _rgb_callback(mario: Mario, t: str):
    event = pygame.event.Event(RGB_EVENT, value=t, sender=mario)
    pygame.event.post(event)

def _pants_callback(mario: Mario, powerup: str):
    event = pygame.event.Event(PANTS_EVENT, value=powerup, sender=mario)
    pygame.event.post(event)

class AsyncClock():
    """Use this instead of pygame.time.Clock when using Lego Mario.
    Your AsyncClock object's tick method must be called once per frame,
    otherwise Mario cannot send events.
    """
    def __init__(self) -> None:
        self.clock = pygame.time.Clock()
        self.get_time = self.clock.get_time
        self.get_rawtime = self.clock.get_rawtime
        self.get_fps = self.clock.get_fps
        self._tick = self.clock.tick
        self.loop = asyncio.get_event_loop()
        self._tick_busy_loop = self.clock.tick_busy_loop
    
    def tick(self, framerate: int = 0) -> int:
        """Limits framerate by blocking, but uses spare time for async loop.

        Args:
            framerate (int, optional): Maximum desired framerate. If 0 or not
                provided, will not delay. Defaults to 0.

        Returns:
            int: The number of milliseconds since last call.
        """
        self.loop.run_until_complete(asyncio.sleep(0.01))
        return self._tick(framerate)

    def tick_busy_loop(self, framerate: int = 0) -> int:
        self.loop.run_until_complete(asyncio.sleep(0.01))
        return self._tick_busy_loop(framerate)

class PygameMario(Mario):
    """Connect to Lego Mario and enable it to post pygame events.
        Lego Mario's events will contain a sender (event.sender), which is the
        Lego Mario object, and a value (event.value), which will either be a
        string (in case of pants or camera data) or a tuple of integers (in
        case of acceleration data)."""
    def __init__(self, enable_acc_events: bool = True,
                 enable_rgb_events: bool = True,
                 enable_pants_events: bool = True,
                 **kwargs) -> None:
        """
        Args:
            enable_acc_events (bool, optional): Whether to send acceleration
                events. event.value will be tuple(int, int, int).
                Be aware that this will send a lot of events.
                Defaults to True.
            enable_rgb_events (bool, optional): Whether to send rgb events
                like RGB tiles or ground color. event.value will be str.
                Defaults to True.
            enable_pants_events (bool, optional): Whether to send pants events.
                event.value will be str. Defaults to True.
        """
        kwargs.setdefault('do_log', False)
        kwargs.setdefault('default_volume', 0)
        super().__init__(**kwargs)
        ports_task = self._init_ports(enable_acc_events, enable_rgb_events,
                                     enable_pants_events)
        asyncio.get_event_loop().create_task(ports_task)

    async def _init_ports(self, acc_enabled: bool, rgb_enabled: bool,
                         pants_enabled: bool) -> None:
        await self.await_connection()
        if acc_enabled:
            self.add_accelerometer_hooks(_acceleration_callback)
        else:
            await self.port_setup(0, 0, False)
        if rgb_enabled:
            self.add_tile_hooks(_rgb_callback)
        else:
            await self.port_setup(1, 0, False)
        if pants_enabled:
            self.add_pants_hooks(_pants_callback)
        else:
            await self.port_setup(2, 0, False)