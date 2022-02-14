# pyLegoMario
pyLegoMario is a little script that connects to Lego Mario and then reads its
acceleromter and tile sensor data.
To connect you have to turn Mario on and then press the Bluetooth Button.
See mario_sample.py for a nice sample.
To disconnect you have to await Mario.disconnect() or await Mario.turn_off(), as well as set Mario._autoReconnect = False


## TL;DR;
"just show me how to use it!"
```python
from pyLegoMario import Mario, MarioWindow, run
# Initialize Mario
mario = Mario()
# Create GUI
MarioWindow(mario)
# call run() to keep asyncio loop running until all tasks are done
run()
```

On Windows you will need Python 3.9 or higher for Bluetooth sockets to work properly.