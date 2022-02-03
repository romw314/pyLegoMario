import ev3_dc as ev3
from thread_task import Sleep
import asyncio
from mario import Mario, create_and_connect_mario

EV3_SETTINGS = {"protocol":ev3.BLUETOOTH, "host":"00:16:53:81:D7:E2"}
with ev3.EV3(**EV3_SETTINGS) as brick:
    with ev3.TwoWheelVehicle(0.02124, 0.1715, ev3_obj=brick) as car:
        speed = 0
        turn = 0
        def my_tile_hook(mario: Mario, t: str):
            """
            Test Function which will be called as soon as a tile is detected by Mario.
            t will contain the Name of the tile that was deteced.
            """
            global speed 
            global turn
            if t == "Goomba":
                speed += 10
                car.move(speed, turn)
            elif t == "BJR":
                speed -= 10
                car.move(speed, turn)
            elif t == "Boo":
                turn += 10
                car.move(speed, turn)
            elif t == "Bob-omb":
                turn -=10
                car.move(speed, turn)
        
        def my_accelerometer_hook(mario: Mario, x: int, y: int, z: int):
            """
            Test Function which will be called for every change in x, y or z accelerometer value.
            """
            car.move(-z, 0)

        def my_pants_hook(mario: Mario, powerup: str):
            """Test function which will be called for every time mario changes pants.

            Args:
                powerup (str): The powerup Mario turns into
            """

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