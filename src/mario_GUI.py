import tkinter as tk
import mario, asyncio
from LEGO_MARIO_DATA import *

class MarioWindow(tk.Frame):
    def __init__(self, mario: mario.Mario, master=None):
        tk.Frame.__init__(self, master)
        self.master.title("Lego Mario")
        self._mario = mario
        self.grid()
        
        # Acceleration Data
        self.xLabel = tk.Label(self, text="X")
        self.yLabel = tk.Label(self, text="Y")
        self.zLabel = tk.Label(self, text="Z")
        self.xLabel.grid(row=0, column=0)
        self.yLabel.grid(row=0, column=1)
        self.zLabel.grid(row=0, column=2)
        # set up StringVars to change fields
        self.xAccText = tk.StringVar()
        self.yAccText = tk.StringVar()
        self.zAccText = tk.StringVar()
        # Create Entries Using StringVars
        self.xAccBox = tk.Entry(self, width=4, state="readonly", textvariable=self.xAccText)
        self.yAccBox = tk.Entry(self, width=4, state="readonly", textvariable=self.yAccText)
        self.zAccBox = tk.Entry(self, width=4, state="readonly", textvariable=self.zAccText)
        # Grid Entries
        self.xAccBox.grid(row=1, column=0)
        self.yAccBox.grid(row=1, column=1)
        self.zAccBox.grid(row=1, column=2)
        # Hook Fields to Mario
        self._mario.AddAccelerometerHook(self.input_acceleration_data)

        # Pants Data
        self.pantsText = tk.StringVar()
        self.pantsBox = tk.Entry(self, width=len(max(HEX_TO_PANTS.values(), key=len)), state="readonly", textvariable=self.pantsText)
        self.pantsBox.grid(row=1, column=3)
        self._mario.AddPantsHook(self.input_pants_data)

        # Ground Data
        self.rgbText = tk.StringVar()
        self.rgbBox = tk.Entry(self, width=len(max(list(HEX_TO_RGB_TILE.values()) + list(HEX_TO_COLOR_TILE.values()), key=len)), state='readonly', textvariable=self.rgbText)
        self.rgbBox.grid(row=1, column=4)
        self._mario.AddTileHook(self.input_rgb_data)

        # Logging Data
        self.LOGBOXWIDTH = 80
        self.logText = tk.StringVar()
        self.logBox = tk.Text(self, state=tk.DISABLED, width=self.LOGBOXWIDTH)
        self.logBox.grid(columnspan=6)
        self._mario.AddLogHook(self.input_log_data)

        # Button for connecting Mario
        self.connectButton = tk.Button(self, text="Connect", command=self.connect_mario)
        self.connectButton.grid()

        # Button for Quitting the window
        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=3, column=1)

        # Scale for Adjusting Volume
        self.volumeVar = tk.IntVar(value=100)
        self.volumeScale = tk.Scale(self, variable=self.volumeVar, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_mario_volume)
        self.volumeScale.grid(row=1, column=5, columnspan=2)

        # display and update the window
        asyncio.get_event_loop().create_task(self.run_window())

    def connect_mario(self):
        """Connect to a Lego Mario device. Will pass if self._mario is already running.
        """
        if not self._mario._run:
            asyncio.create_task(self._mario.connect())
        elif self._mario._client:
            asyncio.create_task(self._mario.disconnect())

    def set_mario_volume(self, volume):
        volume = int(volume)
        asyncio.create_task(self._mario.set_volume(volume))
    
    def input_log_data(self, sender: mario.Mario, msg: str):
        """Function to display log messages in GUI

        Args:
            sender (mario.Mario): The Mario entity that sends the data. Argument is only here for compatibility with mario's event hooks.
            msg (str): Log Message
        """
        assert sender == self._mario
        try:
            content, hex_msg = msg.split(", Hex: ")
            msg = "%s%s" % (content.ljust(self.LOGBOXWIDTH - len(hex_msg)), hex_msg)
        except ValueError:
            pass
        if not msg.startswith("X: "):
            self.logBox['state'] = tk.NORMAL
            self.logBox.insert(tk.END, "\n%s" % msg)
            self.logBox['state'] = tk.DISABLED
            self.logBox.see(tk.END)

    def input_acceleration_data(self, sender: mario.Mario, x: int, y: int, z: int) -> None:
        """Hook for acceleration data to be displayed on GUI

        Args:
            sender (mario.Mario): The Mario entity that sends the data. Argument is only here for compatibility with mario's event hooks.
            x (int): acceleration data in x direction
            y (int): acceleration data in y direction
            z (int): acceleration data in z direction
        """
        assert sender == self._mario
        self.xAccText.set(str(x))
        self.yAccText.set(str(y))
        self.zAccText.set(str(z))
    
    def input_pants_data(self, sender: mario.Mario, pants: str) -> None:
        """Hook for pants data to be displayed on GUI

        Args:
            sender (mario.Mario): The Mario entity that sends the data. Argument is only here for compatibility with mario's event hooks.
            pants (str): The type of pants mario is wearing. See LEGO_MARIO_DATA.py for more info
        """
        assert sender == self._mario
        self.pantsText.set(pants)

    def input_rgb_data(self, sender: mario.Mario, color_or_tile: str) -> None:
        """Hook for rgb/tile data to be displayed on GUI

        Args:
            sender (mario.Mario): The Mario entity that sends the data. Argument is only here for compatibility with mario's event hooks.
            color_or_tile (str): String of the color or tile. See LEGO_MARIO_DATA.py for more info
        """
        assert sender == self._mario
        self.rgbText.set(color_or_tile)

    def quit(self) -> None:
        """Destroys the window and removes Mario's event hooks. Mario remains connected! Call Mario.disconnect() to disconnect.
        """
        # Remove Hooks
        self._mario.RemoveEventsHook((self.input_acceleration_data, self.input_pants_data, self.input_rgb_data, self.input_log_data))
        # Close Window
        self.master.destroy()

    async def run_window(self, interval = 0.05):
        try:
            while True:
                if self._mario._client:
                    self.connectButton.config(text="Disconnect", state=tk.NORMAL)
                    self.volumeScale.config(state=tk.NORMAL)
                    self.master.title("Lego Mario - %s" % self._mario._client.address)
                elif not self._mario._run:
                    self.master.title("Lego Mario - Not Connected")
                    self.connectButton.config(text="Connect", state=tk.NORMAL)
                    self.volumeScale.config(state=tk.DISABLED)
                else:
                    self.master.title("Lego Mario - Connecting...")
                    self.connectButton.config(state=tk.DISABLED)
                    self.volumeScale.config(state=tk.DISABLED)

                self.update()
                await asyncio.sleep(interval)
        except tk.TclError as e:
            if "application has been destroyed" not in e.args[0] and "invalid command name" not in e.args[0]:
                print(e.args)

a = MarioWindow(mario.Mario())
asyncio.get_event_loop().run_forever()