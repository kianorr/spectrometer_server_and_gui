import socket
import zlib
import json
import csv
import numpy as np

# Sends parameters for spectrometer from client
class SendSettings:
    '''Sends parameters for spectrometer settings from client side to server side.
    
    The parameters (`trig_val`, `int_time_micros`) are eventually passed through the SpecInfo class.
    
    Attributes
    ----------
    trig_val (int): Sets trigger mode.
    int_time_micros (int): Integration time in microseconds.
    server_address (list): contains ip address (group) and port number in form [IP, port].
    '''
    def __init__(self, server_address, trig_val, int_time_micros):
        '''Constructor for SendSettings class.
        
        Parameters
        ----------
        trig_val: <int>
            Sets trigger mode:
                normal = 0,
                level/software = 1,
                synchronization = 2,
                edge/hardware = 3
        int_time_micros: <int>
            Integration time in microseconds.
        server_address: <list>
            Contains ip address (group) and port number in form [group, port].
        '''
        self.server_address = server_address
        self.trig_val = trig_val
        self.int_time_micros = int_time_micros
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # Sending chosen spectrometer settings to server side
    def send_settings(self):
        '''Sends parameters to server side to pass through SpecInfo class.'''
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        spec_parameters = [self.trig_val, self.int_time_micros]
        self.sock.sendto(b"%a" % spec_parameters, (self.server_address[0], self.server_address[1]))

    def send_zero_bytes(self):
        '''Sends zero bytes to server.'''
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        b0 = b""
        self.sock.sendto(b0, (self.server_address[0], self.server_address[1]))

    def get_port(self):
        '''Gets the port that was last used after sending.'''
        return self.sock.getsockname()[1]
        
# Receives spectrometer data
class ReceiveSpecData:
    '''Receives spectrometer data from server side.'''
    def __init__(self):
        '''Constructor for Receive class.'''
        self.spectrum_bytes = b""
        self.shape_bytes = b""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    def create_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # Setting socket to receive data
    def set_socket_receive(self, client_port, server_address):
        '''Sets socket option for receiving data.
        
        Parameters
        ----------
        client_port: <int>
            Port that was last used by the client to send data.
        server_address: <list>
            Server address in the form [IP, port]
            
        Notes
        -----
        socket.bind specifies an address and port from which to receive data.
            For sock.bind(('', port)), the port receives on all multicast groups.
            If you want the port receiving on a specific group, then do sock.bind((group, port))
        '''
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
        self.sock.bind((server_address[0], client_port))
    
    def receive_data(self):
        '''Receives spectrum and shape of spectrum.
        
        Receives spectrum data in form of bytes, then receives 0 bytes to break from loop,
        and finally it receives data about the shape of the spectrum array.
        '''
        tf = True
        z = b""
        self.spectrum_bytes = b""
        self.shape_bytes = b""
        while tf == True:
            z = self.sock.recv(1024)
            self.spectrum_bytes += z
            if len(z) == 0:
                tf = False

        # receives shape data
        self.shape_bytes = self.sock.recv(1024)

        #self.sock.close()

        print("The data has been received.")
    
    def prepare_data(self):
        '''Converts spectrum data and shape from bytes to a numpy array and tuple, respectively.
        
        Sometimes, some bytes are lost in the process of sending but it's very minimal
        
        Returns
        -------
        spectrum: <numpy.ndarray>
            In the form `np.array([[wavelengths], [intensities]])`.
        '''
        spec_decompressed = zlib.decompress(self.spectrum_bytes)
        shape = tuple(json.loads(self.shape_bytes))
        spectrum = np.frombuffer(spec_decompressed).reshape(shape)
        return spectrum

    def open_data_csv(self):
        '''Opens csv file that will later be appended to.'''
        with open('mycsv.csv', 'w', newline='') as f:
            fieldnames = ['wavelengths', 'intensities']
            thewriter = csv.DictWriter(f, fieldnames=fieldnames)
            thewriter.writeheader()

    def append_data_csv(self, spectrum):
        '''Appends data to csv file.'''
        with open('mycsv.csv', 'a', newline='') as f:
            fieldnames = ['wavelengths', 'intensities']
            thewriter = csv.DictWriter(f, fieldnames=fieldnames)
            i = 0
            for i in range(len(spectrum[0])):
                thewriter.writerow({'wavelengths' : spectrum[0][i], 'intensities' : spectrum[1][i]})
