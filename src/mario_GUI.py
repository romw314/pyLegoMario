import tkinter as tk
from pathlib import Path
import mario, asyncio
from LEGO_MARIO_DATA import *
from PIL import ImageTk, Image

class MarioWindow(tk.Frame):
    def __init__(self, mario_entity: mario.Mario, master=None):
        self._mario = mario_entity
        tk.Frame.__init__(self, tk.Toplevel() if tk._default_root else master)
        # Window Setup
        self.master.minsize(644, 165)
        self.master.iconbitmap(Path(__file__).parent / "icon.ico")
        bg_image = Image.open(Path(__file__).parent / "background.png")
        self.bg_image_tk = ImageTk.PhotoImage(bg_image)
        background_label = tk.Label(self, image=self.bg_image_tk)
        background_label.place(x=0,y=0, relheight=1, relwidth=1)
        # Resizing Geometry
        self.pack(fill=tk.BOTH, expand=True)
        self.columnconfigure([0,1,2,3],weight=1)
        self.rowconfigure(1,weight=1)

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
        # Variable to Access Pants Data
        self.pantsText = tk.StringVar()
        # Frame to Hold Other Widgets (Not Visible Itself)
        self.pantsFrame = tk.Frame(self)
        # Visible Stuff
        self.pantsLabel = tk.Label(self.pantsFrame, text="Pants") # Purely Descriptive Label, No Interaction
        self.pantsBox = tk.Entry(self.pantsFrame, width=len(max(HEX_TO_PANTS.values(), key=len)), state="readonly", textvariable=self.pantsText)
        
        self.pantsFrame.grid(row=0, column=2) # Grid Frame On Mainframe
        self.pantsLabel.grid(row=0) # Grid Label on pantsFrame
        self.pantsBox.grid(row=1) # Grid Entry on pantsFrame
        # Add Event Hook to Mario
        self._mario.AddPantsHook(self.input_pants_data)

        # RGB Data
        self.rgbText = tk.StringVar()
        self.rgbFrame = tk.Frame(self)
        self.rgbLabel = tk.Label(self.rgbFrame, text="RGB/Tile")
        self.rgbBox = tk.Entry(self.rgbFrame, width=len(max(list(HEX_TO_RGB_TILE.values()) + list(HEX_TO_COLOR_TILE.values()), key=len)), state='readonly', textvariable=self.rgbText)
        self.rgbFrame.grid(row=0, column=1)
        self.rgbLabel.grid(row=0)
        self.rgbBox.grid(row=1)
        self._mario.AddTileHook(self.input_rgb_data)

        # Scale for Adjusting Volume
        self.volumeFrame = tk.Frame(self, bg="#5c94fc")
        self.volumeVar = tk.IntVar(value=100)
        self.volumeScale = tk.Scale(self.volumeFrame, variable=self.volumeVar, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_mario_volume, label="Volume", highlightthickness=0)
        self.volumeFrame.grid(row=0, column=3) # Grid Frame on Mainframe
        self.volumeScale.grid(row=0, column=0) # Grid Scale on volumeFrame

        # Logging Data
        self.logText = tk.StringVar()
        self.logBox = tk.Text(self, state=tk.DISABLED, width=80)
        self.logBox.grid(row=1, columnspan=6, sticky=tk.NSEW)
        self._mario.AddLogHook(self.input_log_data)

        # Frame for Buttons
        self.buttonFrame = tk.Frame(self, bg="#5c94fc")
        self.buttonFrame.grid(row=2, column=0, columnspan=2, sticky=tk.EW)
        self.buttonFrame.columnconfigure([0,1,2],weight=1)

        # Button for connecting Mario
        self.connectButton = tk.Button(self.buttonFrame, text="Connect", command=self.dis_connect_mario)
        self.connectButton.grid(row=0, column=0)

        # Button for Quitting the window
        self.quitButton = tk.Button(self.buttonFrame, text='Quit', command=self.quit)
        self.quitButton.grid(row=0, column=1)

        # Button for Turning Mario off
        self.turnOffButton = tk.Button(self.buttonFrame, text="Turn Off", command=self.turn_mario_off)
        self.turnOffButton.grid(row=0, column=2)

        # Checkbox for AutoReconnect
        self.reconnectVar = tk.IntVar(self, value=1) 
        self.reconnectCheckBox = tk.Checkbutton(self, variable=self.reconnectVar, command=self.set_auto_reconnect, text="Auto-Reconnect")
        self.reconnectCheckBox.grid(row=2, column=2)

        # Request Port Values
        self.portVar = tk.IntVar(self, value=0)
        # Frame for All Content Regarding Port Values
        self.portFrame = tk.Frame(self)
        # Button to Request Value
        self.requestPortValueButton = tk.Button(self.portFrame, text="Request Value", command=lambda: self.request_port(self.portVar.get()))
        # Radiobutton for Each Port (Grid All to portFrame)
        for port in (1,2,3,4,6): # no Port 0 because accelerometer messages aren't printed to Log, no Port 5 because it doesn't exist
            tk.Radiobutton(self.portFrame, variable=self.portVar, value=port, text="Port %s" % port).grid(row=(port-1 )//3, column=(port-1)%3 if port!= 6 else 1)
        self.portFrame.grid(row=2, column=3)
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

    def set_mario_volume(self, placeholder):
        """Creates asyncio task of Mario's set_volume Coroutine.\n
        The new volume is the current value of self.volumeVar (set by the volumeScale).

        Args:
            placeholder (any): This argument is NOT used! It exists only for compatibility with tk.Scale's way of calling its command.
        """
        asyncio.create_task(self._mario.set_volume(self.volumeVar.get()))
    
    def set_auto_reconnect(self):
        """Sets Mario's ._autoReconnect attribute to the current value of self.reconnectVar (determined by self.reconnectCheckBox)."""
        self._mario._autoReconnect = bool(self.reconnectVar.get())

    def turn_mario_off(self):
        """Creates asyncio task of Mario's .turn_off() Coroutine.
        """
        asyncio.create_task(self._mario.turn_off())

    def request_port(self, port: int):
        """Creates asyncio task of Mario's .request_port_value(port) Coroutine.

        Args:
            port (int): The port to be requested. Must be in (0,1,2,3,4,6)
        """
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
            msg = "%s%s" % (content.ljust(self.logBox["width"] - len(hex_msg)), hex_msg)
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
        self._mario._autoReconnect = False
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
                    self.turnOffButton.config(state=tk.NORMAL)
                    self.connectButton.config(text="Disconnect", state=tk.NORMAL)
                    self.volumeScale.config(state=tk.NORMAL)
                    self.master.title("Lego Mario - %s" % self._mario._client.address)
                # Mario is disconnected and not trying to connect
                elif not self._mario._run:
                    self.requestPortValueButton.config(state=tk.DISABLED)
                    self.turnOffButton.config(state=tk.DISABLED)
                    self.master.title("Lego Mario - Not Connected")
                    self.connectButton.config(text="Connect", state=tk.NORMAL)
                    self.volumeScale.config(state=tk.DISABLED)
                # Mario is running, but not connected (currently trying to connect)
                else:
                    self.requestPortValueButton.config(state=tk.DISABLED)
                    self.turnOffButton.config(state=tk.DISABLED)
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
b = MarioWindow(mario.Mario())
while asyncio.all_tasks(loop=asyncio.get_event_loop()):
    asyncio.get_event_loop().run_until_complete(asyncio.gather(*asyncio.all_tasks(loop=asyncio.get_event_loop())))