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
        # Frame for Labels + Entries
        self.accelerationFrame = tk.Frame(self)
        self.accelerationFrame.grid(row=0, column=0)
        # Labels
        self.xLabel = tk.Label(self.accelerationFrame, text="X")
        self.yLabel = tk.Label(self.accelerationFrame, text="Y")
        self.zLabel = tk.Label(self.accelerationFrame, text="Z")
        self.xLabel.grid(row=0, column=0)
        self.yLabel.grid(row=0, column=1)
        self.zLabel.grid(row=0, column=2)
        # StringVars Receiving Data
        self.xAccText = tk.StringVar()
        self.yAccText = tk.StringVar()
        self.zAccText = tk.StringVar()
        # Create Entries Using StringVars
        self.xAccBox = tk.Entry(self.accelerationFrame, width=4, state="readonly", textvariable=self.xAccText)
        self.yAccBox = tk.Entry(self.accelerationFrame, width=4, state="readonly", textvariable=self.yAccText)
        self.zAccBox = tk.Entry(self.accelerationFrame, width=4, state="readonly", textvariable=self.zAccText)
        self.xAccBox.grid(row=1, column=0)
        self.yAccBox.grid(row=1, column=1)
        self.zAccBox.grid(row=1, column=2)
        # Hook Fields to Mario
        self._mario.AddAccelerometerHook(self.input_acceleration_data)

        # Pants Data
        self.pantsFrame = tk.Frame(self)
        self.pantsFrame.grid(row=0, column=2)
        self.pantsLabel = tk.Label(self.pantsFrame, text="Pants")
        self.pantsText = tk.StringVar()
        self.pantsBox = tk.Entry(self.pantsFrame, width=len(max(HEX_TO_PANTS.values(), key=len)), state="readonly", textvariable=self.pantsText)
        self.pantsLabel.grid(row=0)
        self.pantsBox.grid(row=1)
        self._mario.AddPantsHook(self.input_pants_data)

        # RGB Data
        self.rgbFrame = tk.Frame(self)
        self.rgbFrame.grid(row=0, column=1)
        self.rgbLabel = tk.Label(self.rgbFrame, text="RGB/Tile")
        self.rgbText = tk.StringVar()
        self.rgbBox = tk.Entry(self.rgbFrame, width=len(max(list(HEX_TO_RGB_TILE.values()) + list(HEX_TO_COLOR_TILE.values()), key=len)), state='readonly', textvariable=self.rgbText)
        self.rgbLabel.grid(row=0)
        self.rgbBox.grid(row=1)
        self._mario.AddTileHook(self.input_rgb_data)

        # Scale for Adjusting Volume
        self.volumeFrame = tk.Frame(self)
        self.volumeFrame.grid(row=0, column=3)
        self.volumeLabel = tk.Label(self.volumeFrame, text="Volume")
        self.volumeVar = tk.IntVar(value=100)
        self.volumeScale = tk.Scale(self.volumeFrame, variable=self.volumeVar, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_mario_volume)
        self.volumeLabel.grid(row=0, column=5)
        self.volumeScale.grid(row=1, column=5)

        # Logging Data
        self.LOGBOXWIDTH = 80
        self.logText = tk.StringVar()
        self.logBox = tk.Text(self, state=tk.DISABLED, width=self.LOGBOXWIDTH)
        self.logBox.grid(row=1, columnspan=6)
        self._mario.AddLogHook(self.input_log_data)

        # Button for connecting Mario
        self.connectButton = tk.Button(self, text="Connect", command=self.dis_connect_mario)
        self.connectButton.grid(row=2, column=0)

        # Button for Quitting the window
        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=2, column=1)

        # Checkbox for AutoReconnect
        self.reconnectVar = tk.IntVar(self, value=1) 
        self.reconnectCheckBox = tk.Checkbutton(self, variable=self.reconnectVar, command=self.set_auto_reconnect, text="Auto-Reconnect")
        self.reconnectCheckBox.grid(row=2, column=2)

        # Request Port Values
        # Frame for All Content Regarding Port Values
        self.portFrame = tk.Frame(self)
        self.portFrame.grid(row=2, column=3)
        # Radiobutton for Each Port (Grid All to Frame)
        self.portVar = tk.IntVar(self, value=0)
        for port in (1,2,3,4,6): # no Port 0 because accelerometer messages aren't printed to Log
            tk.Radiobutton(self.portFrame, variable=self.portVar, value=port, text="Port %s" % port).grid(row=(port-1 )//3, column=(port-1)%3 if port!= 6 else 1)
        # Button to Request Value
        self.requestPortValueButton = tk.Button(self.portFrame, text="Request Value", command=lambda: self.request_port(self.portVar.get()))
        self.requestPortValueButton.grid(row=1, column=2)

        # display and update the window
        asyncio.get_event_loop().create_task(self.run_window())

    def dis_connect_mario(self):
        """Connects Mario if Mario isn't running. Disconnect Mario if Mario is connected. Passes otherwise (e.g. running but not connected yet)
        """
        if not self._mario._run:
            asyncio.create_task(self._mario.connect())
        elif self._mario._client:
            asyncio.create_task(self._mario.disconnect())

    def set_mario_volume(self, volume):
        asyncio.create_task(self._mario.set_volume(self.volumeVar.get()))
    
    def set_auto_reconnect(self):
        self._mario._autoReconnect = bool(self.reconnectVar.get())

    def request_port(self, port: int):
        asyncio.get_event_loop().create_task(self._mario.request_port_value(port))
    
    def input_log_data(self, sender: mario.Mario, msg: str):
        """Function to display log messages in GUI

        Args:
            sender (mario.Mario): The Mario entity that sends the data. Argument is only here for compatibility with mario's event hooks.
            msg (str): Log Message
        """
        assert sender == self._mario
        try:
            # format message nicely by splitting pure message (Hexadecimal) and human readable string
            content, hex_msg = msg.split(", Hex: ")
            msg = "%s%s" % (content.ljust(self.LOGBOXWIDTH - len(hex_msg)), hex_msg)
        except ValueError:
            # unable to split/format: leave message untouched
            pass
        # Insert Message Into Log Textbox
        if not msg.startswith("X: "):
            self.logBox['state'] = tk.NORMAL
            self.logBox.insert(tk.END, "\n%s" % msg) # insert newline for each message
            self.logBox['state'] = tk.DISABLED
            self.logBox.see(tk.END) # scroll down

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
        # Remove Hooks from Mario
        self._mario.RemoveEventsHook((self.input_acceleration_data, self.input_pants_data, self.input_rgb_data, self.input_log_data))
        # Close Window
        try:
            self.master.destroy()
        except tk.TclError as e:
            pass

    async def run_window(self, interval: float = 0.06) -> None:
        """Endless loop that keeps the window running, updating it every INTERVAL seconds.\n
        This loop is also responsible for enabling and disabling GUI functions depending on Mario's connection status

        Args:
            interval (float, optional): Time interval between window updates. Defaults to 0.06.
        """
        try:
            while True:
                # Mario is connected and running
                if self._mario._client:
                    self.requestPortValueButton.config(state=tk.NORMAL)
                    self.connectButton.config(text="Disconnect", state=tk.NORMAL)
                    self.volumeScale.config(state=tk.NORMAL)
                    self.master.title("Lego Mario - %s" % self._mario._client.address)
                # Mario is disconnected and not trying to connect
                elif not self._mario._run:
                    self.requestPortValueButton.config(state=tk.DISABLED)
                    self.master.title("Lego Mario - Not Connected")
                    self.connectButton.config(text="Connect", state=tk.NORMAL)
                    self.volumeScale.config(state=tk.DISABLED)
                # Mario is running, but not connected (currently trying to connect)
                else:
                    self.requestPortValueButton.config(state=tk.DISABLED)
                    self.master.title("Lego Mario - Connecting...")
                    self.connectButton.config(state=tk.DISABLED)
                    self.volumeScale.config(state=tk.DISABLED)
                # tkinter's update function
                self.update()
                await asyncio.sleep(interval)
        except tk.TclError as e:
            self.quit() # even in case of crash or closed window, remove Mario's event hooks
            if "application has been destroyed" not in e.args[0] and "invalid command name" not in e.args[0]:
                print(e.args) # debug

a = MarioWindow(mario.Mario())
asyncio.get_event_loop().run_forever()