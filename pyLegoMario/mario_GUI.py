import tkinter as tk
from pathlib import Path
import asyncio
from PIL import ImageTk, Image
from .mario import Mario
from .LEGO_MARIO_DATA import *

class MarioWindow(tk.Frame):
    def __init__(self, mario_entity: Mario, master=None):
        self.mario = mario_entity
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

        # Start Acceleration Data
        self.acceleration_frame = tk.Frame(self)
        self.acceleration_frame.grid(row=0, column=0)
        self.x_label = tk.Label(self.acceleration_frame, text="X")
        self.y_label = tk.Label(self.acceleration_frame, text="Y")
        self.z_label = tk.Label(self.acceleration_frame, text="Z")
        self.x_label.grid(row=0, column=0)
        self.y_label.grid(row=0, column=1)
        self.z_label.grid(row=0, column=2)
        # StringVars Receiving Data
        self.x_acceleration_text = tk.StringVar()
        self.y_acceleration_text = tk.StringVar()
        self.z_acceleration_text = tk.StringVar()
        # Create Entries Using StringVars
        self.x_acceleration_box = tk.Entry(self.acceleration_frame, width=4,
                    state="readonly", textvariable=self.x_acceleration_text)
        self.y_acceleration_box = tk.Entry(self.acceleration_frame, width=4,
                    state="readonly", textvariable=self.y_acceleration_text)
        self.z_acceleration_box = tk.Entry(self.acceleration_frame, width=4,
                    state="readonly", textvariable=self.z_acceleration_text)
        self.x_acceleration_box.grid(row=1, column=0)
        self.y_acceleration_box.grid(row=1, column=1)
        self.z_acceleration_box.grid(row=1, column=2)
        # Hook Fields to Mario
        self.mario.add_accelerometer_hooks(self.input_acceleration_data)
        # End Acceleration Data

        # Start Pants Data
        # Static container (invisible frame) and description label
        self.pants_frame = tk.Frame(self)
        self.pants_label = tk.Label(self.pants_frame, text="Pants")
        # Variable and Entry for Displaying Variable
        self.pants_text = tk.StringVar()
        self.pants_box = tk.Entry(self.pants_frame, 
                                width=len(max(HEX_TO_PANTS.values(), key=len)),
                                state="readonly", textvariable=self.pants_text)
        
        self.pants_frame.grid(row=0, column=2)
        self.pants_label.grid(row=0)
        self.pants_box.grid(row=1)
        # Hook Field to Mario
        self.mario.add_pants_hooks(self.input_pants_data)
        # End Pants Data

        # Start RGB Data
        self.rgbFrame = tk.Frame(self)
        self.rgbLabel = tk.Label(self.rgbFrame, text="RGB/Tile")
        self.rgbText = tk.StringVar()
        possible_values = (HEX_TO_RGB_TILE | HEX_TO_COLOR_TILE).values()
        max_length = max([len(x) for x in possible_values])
        self.rgbBox = tk.Entry(self.rgbFrame, width=max_length,
                                state='readonly', textvariable=self.rgbText)
        self.rgbFrame.grid(row=0, column=1)
        self.rgbLabel.grid(row=0)
        self.rgbBox.grid(row=1)
        # Hook Field to Mario
        self.mario.add_tile_hooks(self.input_rgb_data)
        # End RGB Data

        # Scale for Adjusting Volume
        self.volumeFrame = tk.Frame(self, bg="#5c94fc")
        self.volumeScale = tk.Scale(self.volumeFrame,
                                    from_=0, to=100, orient=tk.HORIZONTAL,
                                    command=self.set_mario_volume,
                                    label="Volume", highlightthickness=0)
        self.volumeFrame.grid(row=0, column=3)
        self.volumeScale.grid(row=0, column=0)

        # Logging Data
        self.logText = tk.StringVar()
        self.logBox = tk.Text(self, state=tk.DISABLED, width=80)
        self.logBox.grid(row=1, columnspan=6, sticky=tk.NSEW)
        self.mario.add_log_hooks(self.input_log_data)

        # Start Buttons
        # Button Container
        self.buttonFrame = tk.Frame(self, bg="#5c94fc")
        self.buttonFrame.grid(row=2, column=0, columnspan=2, sticky=tk.EW)
        self.buttonFrame.columnconfigure([0,1,2],weight=1)

        # This Button will also handle disconnecting
        self.connectButton = tk.Button(self.buttonFrame, text="Connect",
                                        command=self.dis_connect_mario)
        self.connectButton.grid(row=0, column=0)

        self.quit_button = tk.Button(self.buttonFrame, text='Quit',
                                    command=self.quit)
        self.quit_button.grid(row=0, column=1)

        self.turnOffButton = tk.Button(self.buttonFrame, text="Turn Off",
                                        command=self.turn_mario_off)
        self.turnOffButton.grid(row=0, column=2)
        # End Buttons

        # Checkbox for AutoReconnect
        self.reconnectVar = tk.IntVar(self, value=1) 
        self.reconnectCheckBox = tk.Checkbutton(self, text="Auto-Reconnect",
            variable=self.reconnectVar, command=self.set_auto_reconnect)
        self.reconnectCheckBox.grid(row=2, column=2)

        # Frame for port formatting
        self.portFormatFrame = tk.Frame(self, bg="#5c94fc")
        self.portFormatFrame.grid(row=3, column=3)

        # Checkbox for notifications
        self.notificationVar = tk.IntVar(self, value=1)
        self.notificationCheckBox = tk.Checkbutton(
            self.portFormatFrame, variable=self.notificationVar,
            text="Notifications")
        self.notificationCheckBox.grid(column=1, row=0)

        # OptionMenu for port modes
        self.port_mode_variable = tk.StringVar(self)
        options = ("0","1")
        self.mode_menu = tk.OptionMenu(self.portFormatFrame,
                                        self.port_mode_variable,
                                        *options)
        self.mode_menu.config(highlightthickness=0)
        self.port_mode_variable.set("0")
        self.mode_menu.grid(column=0, row=0)

        # Button for configuring port format
        self.portFormatButton = tk.Button(self.portFormatFrame, 
                                        text="Update Port", 
                                        command=self.set_port_input_format)
        self.portFormatButton.grid(column=2, row=0)

        # Request Port Values
        self.portVar = tk.IntVar(self, value=1)
        # Frame for All Content Regarding Port Values
        self.portFrame = tk.Frame(self)
        # Button to Request Value
        self.request_port_button = tk.Button(self.portFrame, 
            text="Request Value", command=self.request_port)
        # Radiobutton for Each Port (Grid All to portFrame)
        # no Port 0/5 (accelerometer isn't printed to Log, Port 5 doesn't exist)
        for i, port in enumerate((1,2,3,4,6)):
            radiobutton = tk.Radiobutton(self.portFrame, 
                            variable=self.portVar, value=port,
                            text=f"Port {port}", command=self.update_mode_menu)
            radiobutton.grid(row=i // 3, column=i % 3)
        self.portFrame.grid(row=2, column=3)
        self.request_port_button.grid(row=1, column=2)

        # display and update the window
        asyncio.get_event_loop().create_task(self.run_window())

    def update_mode_menu(self) -> None:
        """Update the port mode menu with the available port modes for the
        selected port. Called every time a different port gets selected.
        """
        new_choices = VALID_PORT_MODES[self.portVar.get()]

        # change menu accordingly
        self.mode_menu['menu'].delete(0, tk.END)
        for choice in new_choices:
            self.mode_menu['menu'].add_command(
                label=str(choice), 
                command=tk._setit(self.port_mode_variable, str(choice)))

        # only reset selection if previously selected mode is not valid
        if not int(self.port_mode_variable.get()) in new_choices:
            self.port_mode_variable.set("0")

    def set_port_input_format(self) -> None:
        self.mario.port_setup(port=self.portVar.get(), 
                              mode=self.port_mode_variable.get(),
                              notifications=self.notificationVar.get())

    def dis_connect_mario(self) -> None:
        """Connects Mario if Mario isn't running. Disconnect Mario if Mario is
        connected. Passes otherwise (e.g. running but not connected yet)
        """
        if not self.mario.run:
            asyncio.create_task(self.mario.connect())
        elif self.mario.client:
            asyncio.create_task(self.mario.disconnect())

    def set_mario_volume(self, placeholder):
        """Creates asyncio task of Mario's set_volume Coroutine.
        The new volume is the current value of self.volumeVar (set by the volumeScale).

        Args:
            placeholder (any): This argument is NOT used! It exists only for
                compatibility with tk.Scale's way of calling its command.
        """
        self.mario.default_volume = int(placeholder)
        self.mario.set_volume(self.mario.default_volume)
    
    def set_auto_reconnect(self):
        """Sets Mario's ._autoReconnect attribute to the current value of 
        self.reconnectVar (determined by self.reconnectCheckBox)."""
        self.mario.auto_reconnect = bool(self.reconnectVar.get())

    def turn_mario_off(self):
        """Creates asyncio task of Mario's .turn_off() Coroutine.
        """
        asyncio.create_task(self.mario.turn_off())

    def request_port(self) -> None:
        """Requests the currently selected port of Mario.
        """
        port_id = self.portVar.get()
        loop = asyncio.get_event_loop()
        loop.create_task(self.mario.request_port_value(port_id))

    def input_log_data(self, sender: Mario, msg: str) -> None:
        """Function to display log messages in GUI

        Args:
            sender (Mario): The Mario entity that sends the data.
                Used for compatibility with Mario's event hooks.
            msg (str): Log Message
        """
        assert sender == self.mario
        try:
            content, hex_msg = msg.split(", Hex: ")
            msg = f"{content.ljust(self.logBox['width'] - len(hex_msg))}{hex_msg}"
        except ValueError:
            # unable to split/format: leave message untouched
            pass
        # Insert Message Into Log Textbox (excluding acceleration data)
        if not msg.startswith("X: "):  # and "port 3" in msg.lower()
            self.logBox['state'] = tk.NORMAL
            self.logBox.insert(tk.END, f"\n{msg}")
            self.logBox['state'] = tk.DISABLED
            self.logBox.see(tk.END)  # scroll down

    def input_acceleration_data(self, sender: Mario, x: int, y: int, z: int) -> None:
        """Hook for acceleration data to be displayed on GUI

        Args:
            sender (Mario): The Mario entity that sends the data.
                Only used for compatibility with mario's event hooks.
            x (int): acceleration data in x direction
            y (int): acceleration data in y direction
            z (int): acceleration data in z direction
        """
        assert sender == self.mario
        self.x_acceleration_text.set(str(x))
        self.y_acceleration_text.set(str(y))
        self.z_acceleration_text.set(str(z))

    def input_pants_data(self, sender: Mario, pants: str) -> None:
        """Hook for pants data to be displayed on GUI

        Args:
            sender (Mario): The Mario entity that sends the data.
                Only used for compatibility with mario's event hooks.
            pants (str): The type of pants mario is wearing. See LEGO_MARIO_DATA.py for more info
        """
        assert sender == self.mario
        self.pants_text.set(pants)

    def input_rgb_data(self, sender: Mario, color_or_tile: str) -> None:
        """Hook for rgb/tile data to be displayed on GUI

        Args:
            sender (Mario): The Mario entity that sends the data. 
                Only used for compatibility with mario's event hooks.
            color_or_tile (str): String of the color or tile. See LEGO_MARIO_DATA.py for more info
        """
        assert sender == self.mario
        self.rgbText.set(color_or_tile)

    def quit(self) -> None:
        """Destroys the window and removes Mario's event hooks. 
        Mario remains connected. Call Mario.disconnect() to disconnect.
        """
        # Remove Hooks from Mario
        self.mario.remove_hooks((
            self.input_acceleration_data, self.input_pants_data, 
            self.input_rgb_data, self.input_log_data))
        self.mario.auto_reconnect = False
        # Close Window
        try:
            self.master.destroy()
        except tk.TclError as e:
            pass

    async def run_window(self, interval: float = 0.06) -> None:
        """Endless loop that keeps the window running, updating it every
        INTERVAL seconds.\n
        This loop is also responsible for enabling and disabling GUI functions
        depending on Mario's connection status

        Args:
            interval (float, optional): Time interval between window updates.
            Defaults to 0.06.
        """
        try:
            while True:
                # Mario is connected and running
                if self.mario.is_connected:
                    self.request_port_button.config(state=tk.NORMAL)
                    self.portFormatButton.config(state=tk.NORMAL)
                    self.turnOffButton.config(state=tk.NORMAL)
                    self.connectButton.config(text="Disconnect", state=tk.NORMAL)
                    self.master.title(f"Lego Mario - {self.mario.client.address}")
                # Mario is disconnected and not trying to connect
                elif not self.mario.run:
                    self.request_port_button.config(state=tk.DISABLED)
                    self.portFormatButton.config(state=tk.DISABLED)
                    self.turnOffButton.config(state=tk.DISABLED)
                    self.master.title("Lego Mario - Not Connected")
                    self.connectButton.config(text="Connect", state=tk.NORMAL)
                # Mario is running, but not connected (trying to connect)
                else:
                    self.request_port_button.config(state=tk.DISABLED)
                    self.portFormatButton.config(state=tk.DISABLED)
                    self.turnOffButton.config(state=tk.DISABLED)
                    self.master.title("Lego Mario - Connecting...")
                    self.connectButton.config(state=tk.DISABLED)
                # tkinter's update function
                self.update()
                await asyncio.sleep(interval)
        except tk.TclError as e:
            self.quit() # even in case of crash or closed window, remove Mario's event hooks
            if "application has been destroyed" not in e.args[0] and "invalid command name" not in e.args[0]:
                print(e.args) # debug