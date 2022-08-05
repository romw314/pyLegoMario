# pyLegoMario
```pip install pyLegoMario```

pyLegoMario is a script that connects to Lego Mario and reads its acceleromter,
tile sensor, and pants data.
To connect, you have to turn Mario on and then press the Bluetooth Button.
See mario_sample.py for a nice sample.
To disconnect you have to await Mario.disconnect() or await Mario.turn_off(),
as well as set Mario.autoReconnect = False


## TL;DR; "just show me how to use it!"
### The Basics
```python
from pyLegoMario import Mario, MarioWindow, run
# Initialize Mario
mario = Mario()
# Create GUI
MarioWindow(mario)
# call run() at the end of your program to keep the asyncio loop running
run()
```
### Use Mario in Your Own Programs With Callback Functions
```python
def my_pants_hook(mario: Mario, powerup: str) -> None:
    print(f"I'm wearing {powerup} pants!")

mario.add_pants_hook(my_pants_hook)
```
### Use Mario as a Controller in Pygame!
```python
import pygame
from pyLegoMario import PygameMario, AsyncClock
from pyLegoMario import ACC_EVENT, PANTS_EVENT, RGB_EVENT

pygame.init()
mario = PygameMario()
# use AsyncClock instead of pygame.time.Clock
clock = AsyncClock()
screen = pygame.display.set_mode(1200,600)
font = pygame.font.SysFont(None, 48)

while True:
    clock.tick()
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == RGB_EVENT:
            screen.fill((0,0,0))
            # write the current camera value onto the screen
            text = font.render(event.value, True, (255,255,255))
            screen.blit(text, (10,10))
# no need to call run() here, AsyncClock handles this
```
## You Can Do a Lot More!
Sample scripts can be found in the [Github Repository](https://github.com/Jackomatrus/pyLegoMario)

Tweet at me: [@Jackomatrus](https://www.twitter.com/Jackomatrus)

On Windows you will need Python 3.9 or higher for Bluetooth sockets to work properly.

I tested this on Mac and Windows. I have not tested this on Linux.