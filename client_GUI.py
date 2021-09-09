#
# Creates GUI using methods from client.py
#

# For GUI
from tkinter.constants import BOTTOM, CENTER, LEFT, TOP, RIGHT
import tkinter as tk

# Client code
from client import SendSettings, ReceiveSpecData

# For plotting in GUI
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt


class SpecApp(tk.Frame, SendSettings, ReceiveSpecData):
    '''Creates GUI
    
    Attributes
    ----------
    root (class 'tkinter.Tk)
    '''
    def __init__(self, root):
        '''Constructor method for App class.
        
        Creates setting entries, a quit button, and a plot for the GUI.
        
        Parameters
        ----------
        root: <class 'tkinter.Tk'>
        '''
        # Initializing tkinter Frame class.
        tk.Frame.__init__(self, root)
        # Initializing SendParameters class from client.py
        SendSettings.__init__(self, server_address=[], trig_val=0, int_time_micros=0)
        # Initializing Receive class from client.py
        ReceiveSpecData.__init__(self)

        # Not sure what this is, but it packs the GUI frame or something
        self.root = root
        self.pack()

        # Opens csv to write data to
        # ReceiveSpecData().open_data_csv()

        # tells program that there is no re-entry
        self.re_entry = False

        # Creates the spectrum plot
        self.create_plot()

        # creates entries
        trig_entry = self.create_entry("Trigger Value", 0)
        int_entry = self.create_entry("Integration Time (\u03BCs)", 1000)
        ip_entry = self.create_entry("Server IP", '127.0.0.1')
        port_entry = self.create_entry("Server Port", 5004)
        self.setting_entries = [trig_entry, int_entry, ip_entry, port_entry]
        
        # Creates the "quit" button
        self.create_button("Quit", self._quit)

    def create_button(self, text, command):
        '''Creates and packs a button.'''
        button = tk.Button(master=self.root, text=text, command=command)
        button.pack(side=tk.BOTTOM, pady=20)

    def create_plot(self):
        '''Creates and packs embedded plot.'''
        self.fig = plt.Figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Wavelengths")
        self.ax.set_ylabel("Intensities")
        self.ax.set_title("Spectrum")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=1, pady=20, padx=0)

    def create_entry(self, entry, default, ypad=None):
        '''Creates an entry for an int variable.
        
        Parameters
        ----------
        entry: <str>
            Name of label.
        default: <int> or <str>
            Default value for entries.
            
        Returns
        -------
        entry_thingy: <class 'tkinter.Entry'>
        '''
        # creates label
        self.label = tk.Label(text=entry)

        # creates entry
        self.entry_thingy = tk.Entry()

        # packs label and entry so they show up
        self.label.pack(pady=0, padx=0)
        self.entry_thingy.pack(pady=0, padx=30)

        # setting default
        self.contents = tk.IntVar()
        self.contents.set(default)
        self.entry_thingy["textvariable"] = self.contents

        # binding enter/return key to storing parameters and animation
        self.entry_thingy.bind('<Key-Return>', self.start_collection)

        return self.entry_thingy

    def start_collection(self, event):
        '''Stores user's inputs into a list and uses those inputs to send and receive data, which
        is used to create an animation.

        This method is activated when the return key is hit.

        Parameters
        ----------
        event: <class 'tkinter.Event'>

        Notes
        -----
        I know this method is doing a lot of things but I'm not sure if there's a good way to get
        around that because that event parameter does not make it very flexible.
        '''
        setting_list = []

        # goes through length of setting_entries and appends entries to list
        for self.contents in self.setting_entries:
            setting_list.append(self.contents.get())

        # settings for spectrometer
        trig_val = int(setting_list[0])
        int_time_micros = int(setting_list[1])
        server_address = [setting_list[2], int(setting_list[3])]

        self.create_animation(server_address, trig_val, int_time_micros)

    def create_animation(self, server_address, trig_val, int_time_micros):
        # Initializing class that sends inputted setting to server.
        self.s = SendSettings(server_address, trig_val, int_time_micros)

        # Initializing class that receives spectrum data.
        self.r = ReceiveSpecData()
        self.s.send_settings()
        client_port = self.s.get_port()

        # Creates animation
        ani = FuncAnimation(self.fig, 
                            self.animate, 
                            fargs=(self.s, self.r, server_address,client_port,), 
                            interval=100,
                            cache_frame_data=True,
                            save_count=100,
                            frames=10)

        self.canvas.draw()

        # prevents from multiple animations running at once
        if self.re_entry == True:
            ani.event_source.stop()

        self.re_entry = True

    def animate(self, i, send, receive, server_address, client_port):
        '''Continuously receives data from server and plots it.
        
        Used to animate spectrum received from spectrometer. Uses methods from the `SendSettings` and
        `ReceiveSpecData` classes. Every time the method loops around, it sends zero bytes to the server to indicate
        that it should continue sending data.

        Parameters
        ----------
        i: <int>
            Needed for FuncAnimation.
        server_address: <list>
            List in the form of [IP, port]. The IP and port are the server's IP and port.
        client_port: <int>
            This is the port that the client has been assigned (after sending something) to receive data.
        '''
        # Sends zero bytes to server so the server knows when to continue sending data.
        send.send_zero_bytes()
        receive.create_socket()

        # Receiving data
        receive.set_socket_receive(client_port, server_address)
        receive.receive_data()
        spec = receive.prepare_data()
        #receive.append_data_csv(spec)

        # Clearing and then plotting
        self.ax.cla()
        self.ax.set_xlabel("Wavelengths")
        self.ax.set_ylabel("Intensities")
        self.ax.set_title("Spectrum {}".format(i))
        self.ax.plot(spec[0], spec[1])

    def _quit(self):
        '''Closes the window and stops the mainloop.'''
        self.root.quit()     # stops mainloop
        self.root.destroy()
