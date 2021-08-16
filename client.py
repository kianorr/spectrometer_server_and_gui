import socket
import struct
import zlib
import json
import numpy as np

# Sends parameters for spectrometer from client
class SendParameters:
    '''Sends parameters for spectrometer settings from client side to server side.
    
    The parameters (trig_val, int_time, device_num) are passed through the SpecInfo class.
    
    Attributes
    ----------
    trig_val (int): Sets trigger mode.
    int_time (int): Integration time in microseconds.
    device_num (int): Sets which device you want to use if there are multiple. If there is only one, then choose 0.
    address (list): contains ip address (group) and port number in form [group, port].
    '''
    def __init__(self, address, trig_val, int_time, device_num):
        '''Constructor for SendParameters class.
        
        Parameters
        ----------
        trig_val: <int>
            Sets trigger mode:
                normal = 0
                level/software = 1
                synchronization = 2
                edge/hardware = 3
                More information for trigger modes at
                https://www.oceaninsight.com/globalassets/catalog-blocks-and-images/manuals--instruction-old-logo/electronic-accessories/external-triggering-options_firmware3.0andabove.pdf
        int_time: <int>
            Integration time in microseconds.
        device_num: <int>
            Sets which device you want to use if there are multiple. If there is only one, then choose 0.
        address: <list>
            Contains ip address (group) and port number in form [group, port].
        '''
        self.address = address
        self.trig_val = trig_val
        self.int_time = int_time
        self.device_num = device_num
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # Sending chosen spectrometer settings to server side
    def send_parameters(self):
        '''Sends parameters to server side to pass through SpecInfo class.'''
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        spec_parameters = [self.trig_val, self.int_time, self.device_num]
        self.sock.sendto(b"%a" % spec_parameters, (self.address[0], self.address[1]))
        
# Receives spectrometer data
class Receive:
    '''Receives spectrometer data from server side.
    
    Attributes
    ----------
    address (list): contains ip address (group) and port number in form [group, port].
    '''
    def __init__(self, address):
        '''Constructor for Receive class.
        
        Parameters
        ----------
        address: <list>
            Contains ip address (group) and port number in form [group, port].
        '''
        self.spectrum_bytes = b""
        self.shape_bytes = b""
        self.address = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # Setting socket to receive data
    def set_socket_receive(self):
        '''Sets socket option for receiving data.'''
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.address[1]))
        mreq = struct.pack("4sl", socket.inet_aton(self.address[0]), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    def receive_data(self):
        '''Receives spectrum and shape of spectrum.
        
        Receives spectrum data in form of bytes, then receives 0 bytes to break from loop,
        and finally it receives data about the shape of the spectrum array.
        '''
        tf = True
        z = b""
        while tf == True:
            z = self.sock.recv(4096)
            self.spectrum_bytes += z
            if len(z) == 0:
                tf = False

        # receives shape data
        self.shape_bytes = self.sock.recv(1024)

        self.sock.close()

        print("The data has been received.")
    
    def prepare_data(self):
        ''' Converts spectrum data and shape from bytes to a numpy array and tuple, respectively.
        
        Sometimes, some bytes are lost in the process of sending but it's very minimal
        
        Returns
        -------
        spectrum: <numpy.ndarray>
            In the form np.array([[wavelengths], [intensities]]).
        '''
        spec_decompressed = zlib.decompress(self.spectrum_bytes)
        shape = tuple(json.loads(self.shape_bytes))
        spectrum = np.frombuffer(spec_decompressed).reshape(shape)
        return spectrum
