import socket
import struct
import json
import math
import numpy as np
from specDataClass import SpecInfo

# Receives parameters for spectrometer settings from client
class ReceiveParameters:
    '''Receives parameters (trig_val, int_time, device_num) from client for adjusting spectrometer settings.
    
    Attributes
    ----------
    address (list): contains ip address (group) and port number in form [group, port]
    '''
    def __init__(self, address):
        '''Constructor for ReceiveParameters class.
        
        Parameters
        ----------
        address: <list>
            contains ip address (group) and port number in form [group, port].
        '''
        self.address = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # Setting up for receiving
    def set_socket_receive(self):
        '''Sets socket option for receiving data.
        
        Notes
        -----
        socket.bind specifies an address and port from which to receive data.
            For sock.bind(('', port)), the port receives on all multicast groups.
            If you want the port receiving on a specific group, then do sock.bind((group, port))
        '''
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.address[1]))
        mreq = struct.pack("4sl", socket.inet_aton(self.address[0]), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    # Received in bytes then converted
    def receive_parameters(self):
        '''Receives spectrometer parameters (trig_val, int_time, device_num) from client.
        
        Converts parameters from bytes to the original list sent from client.
        
        Returns
        -------
        SpecInfo_parameters: <list>
            In form of [trig_val, int_time, device_num].
        '''
        spec_parameters_bytes = self.sock.recv(4096)
        spec_parameters = json.loads(spec_parameters_bytes)
        return spec_parameters

# Sends spectrometer data to client
class Server(SpecInfo):
    def __init__(self, chunk_size, address, ttl, trig_val, int_time, device_num):
        ''' Constructor for Server class.
        
        Parameters
        ----------
        chunk_size: <int>
            Determines how many bytes are sent at a time.
        address: <list>
            contains ip address (group) and port number in form [group, port].
        ttl: <int>
            Time that a datagram has to live in the network.
        trig_val: <int>
            Sets trigger mode.
        int_time: <int>
            Sets integration time in microseconds.
        device_num: <int>
            Sets which device you want to use if there are multiple. If there is only one, then choose 0.
        
        Notes
        -----
        As of right now, trig_val, int_time, and device_num have to be set in the client.
        '''
        SpecInfo.__init__(self, trig_val, int_time, device_num)
        SpecInfo.get_spec(self)
        self.chunk_size = chunk_size
        self.address = address
        self.ttl = ttl
        self.spectrum = b""
        self.shape = ()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # Setting socket to be able to send data
    def set_socket_send(self):
        '''Sets socket option for receiving data.'''
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.ttl)
        
    def get_data(self):
        ''' Gets spectrum data from SpecInfo class.
        
        Returns
        -------
        spectrumCompressed: <bytes>
        '''
        self.spectrum = SpecInfo.get_spec_compressed(self)
        self.shape = list(SpecInfo.get_shape(self))
        return self.spectrum

    def send_data(self):
        '''Sends the compressed spectrum data, an empty bytes string, and the shape of the original np array.
        
        An empty bytes string is sent over to the client so the client knows when to stop receiving data.
        '''
        # Sending over spectrum data by chunk
        b = b""
        i = 0
        for i in range(math.ceil(len(self.spectrum) / self.chunk_size)):
            b = self.spectrum[i * self.chunk_size:(i + 1) * self.chunk_size]
            self.sock.sendto(b, (self.address[0], self.address[1]))
            
        # Sending over 0 bytes so recv loop knows when to stop
        b0 = b""
        self.sock.sendto(b0, (self.address[0], self.address[1]))

        # Sending over shape for reshaping
        self.sock.sendto(b"%a" % self.shape, (self.address[0], self.address[1]))
        
        self.sock.close()
