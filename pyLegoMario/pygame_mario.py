"""
pygame_mario.py
This file implements class PygameMario that subclasses Mario to utilize pygame
events. This file can also be executed as an example of how to write a pygame
game loop with asyncio (which is needed to play with Mario).
Copyright (c) 2022 Bruno Hautzenberger, Jamin Kauf
"""
import sys
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

def acceleration_callback(mario: Mario, x: int, y: int, z: int):
    event = pygame.event.Event(ACC_EVENT, value=(x,y,z), sender=mario)
    pygame.event.post(event)

def rgb_callback(mario: Mario, t: str):
    event = pygame.event.Event(RGB_EVENT, value=t, sender=mario)
    pygame.event.post(event)

def pants_callback(mario: Mario, powerup: str):
    event = pygame.event.Event(PANTS_EVENT, value=powerup, sender=mario)
    pygame.event.post(event)

class PygameMario(Mario):
    def __init__(self, enable_acc_events: bool = True,
                 enable_rgb_events: bool = True,
                 enable_pants_events: bool = True,
                 volume = 0) -> None:
        """Connect to Lego Mario and enable it to post pygame events.
        Lego Mario's events will contain a sender (event.sender), which is the
        Lego Mario object, and a value (event.value), which will either be a
        string (in case of pants or camera data) or a tuple of integers (in
        case of acceleration data).

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
            volume (int, optional): % volume that the device will be set to.
                Defaults to 0.
        """
        super().__init__(False, default_volume=volume)
        ports_task = self.init_ports(enable_acc_events, enable_rgb_events,
                                     enable_pants_events)
        asyncio.create_task(ports_task)

    async def init_ports(self, acc_enabled: bool, rgb_enabled: bool,
                         pants_enabled: bool) -> None:
        await self.await_connection()
        if acc_enabled:
            self.add_accelerometer_hooks(acceleration_callback)
        else:
            await self.port_setup(0, 0, False)
        if rgb_enabled:
            self.add_tile_hooks(rgb_callback)
        else:
            await self.port_setup(1, 0, False)
        if pants_enabled:
            self.add_pants_hooks(pants_callback)
        else:
            await self.port_setup(2, 0, False)

# if you write your own game file, you'll need to use the following import
# from pyLegoMario import PygameMario, ACC_EVENT, RGB_EVENT, PANTS_EVENT
async def run_window():
    pygame.init()
    window = pygame.display.set_mode((1500,800))
    clock = pygame.time.Clock()
    mario = PygameMario(volume=30)
    hspeed = vspeed = 0
    player = pygame.draw.rect(window, (255,255,255), (600,300,100,100))
    while True:
        await asyncio.sleep(0.01)
        clock.tick(60)
        for event in pygame.event.get():
            print(event)
            if event.type == QUIT:
                await mario.disconnect()
                pygame.quit()
                sys.exit()
            elif event.type == ACC_EVENT:
                hspeed, vspeed = event.value[::2]
            elif event.type == RGB_EVENT:
                if 'start' in event.value.lower():
                    player.w += 5
                    player.h += 5
        window.fill((0,0,0))
        player.right += hspeed
        player.top += vspeed
        
        pygame.draw.rect(window, (255,255,255), player)
        pygame.display.update()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run_window())