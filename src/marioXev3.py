import ev3_dc as ev3
from thread_task import Sleep
import asyncio
from mario import Mario, create_and_connect_mario

EV3_SETTINGS = {"protocol":ev3.BLUETOOTH, "host":"00:16:53:81:D7:E2"}
with ev3.EV3(**EV3_SETTINGS) as brick:
    with ev3.TwoWheelVehicle(0.04747, 0.1224, ev3_obj=brick) as car:
        with ev3.Motor(ev3.PORT_C, ev3_obj=brick) as small_motor:
            with ev3.Gyro(ev3.PORT_1, ev3_obj=brick) as gyro:
                small_motor.move_by(3600, speed=80).start(thread=False)
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
                    elif t == "Boom Boom":
                        print(gyro.angle)
            
            def my_accelerometer_hook(mario: Mario, x: int, y: int, z: int):
                """
                Test Function which will be called for every change in x, y or z accelerometer value.
                """
                car.move(-z, x)

            def my_pants_hook(mario: Mario, powerup: str):
                """Test function which will be called for every time mario changes pants.

                Args:
                    powerup (str): The powerup Mario turns into
                """

            async def main():
                NUM_PLAYERS = 1

                # Initialize Marios
                print("Turn on Mario and press Bluetooth Button")
                marios = [Mario(doLog = True, accelerometerEventHooks = my_accelerometer_hook, tileEventHooks = my_tile_hook, pantsEventHooks=None) for player in range(NUM_PLAYERS)]
                
                # Add Hook Functions
                marios[0].AddPantsHook(my_pants_hook)

                loop = asyncio.get_event_loop()
                # loop.create_task(SOME COROUTINE)

            if __name__ == "__main__":
                loop = asyncio.get_event_loop()
                loop.create_task(main())
                loop.run_forever()