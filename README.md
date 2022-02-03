# pyLegoMario
src/mario.py is a little script that connects to Lego Mario and then reads its
acceleromter and tile sensor data. It does so until you call Stop() and turn of 
Mario.
To connect you have to turn Mario on and then press the Bluetooth Button.
See src/mario_sample.py for a logging sample on how to use it (outputting all data Mario receives)


## TL;DR;
"just show me how to use it!"
```python
# Initialize Mario
print("Turn on Mario and press Bluetooth Button")
mario = await create_and_connect_mario()

# Add Hook Functions
mario.AddAccelerometerHook(my_accelerometer_hook)
mario.AddTileHook(my_tile_hook)

loop = asyncio.get_event_loop()
# loop.create_task(SOME COROUTINE)
```

On Windows you will need Python 3.9 or higher for Bluetooth sockets to work properly.