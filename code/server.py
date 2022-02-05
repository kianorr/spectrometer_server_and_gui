import socket
import math
from specDataClass import SpecInfo

# Receives parameters for spectrometer settings from client
class ReceiveSettings:
    '''Receives parameters (`trig_val`, `int_time_micros`) from client for adjusting spectrometer settings.
    
    Attributes
    ----------
    server_address (list): contains ip address (group) and port number in form `[group, port]`
    '''
    def __init__(self, server_address):
        '''Constructor for ReceiveParameters class.
        
        Parameters
        ----------
        server_address: <list>
            contains server ip address (group) and port number in form [IP, port].
        '''
        self.server_address = server_address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # Setting up for receiving
    def set_socket_receive(self):
        '''Sets socket option for reusing address and binds socket to the server address.
        
        Notes
        -----
        socket.bind specifies an address and port from which to receive data.
            For sock.bind(('', port)), the port receives on all multicast groups.
            If you want the port receiving on a specific group, then do sock.bind((group, port))
        '''
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.server_address)
    
    # Received in bytes then converted
    def receive_settings(self):
        '''Receives spectrometer parameters (trig_val, int_time_micros) from client.
        
        Converts parameters from bytes to the original list sent from client.
        
        Returns
        -------
        received_data: <bytes>
            Could be zero bytes or the spectrometer settings in bytes
        client_address: <>
            Address of the client from which the data came from.
        '''
        received_data, client_address = self.sock.recvfrom(4096)
        return received_data, client_address

# Sends spectrometer data to client
class SendSpecData(SpecInfo):
    '''Sends spectrum data to client.
    
    Parameters
    ----------
    chunk_size (int): Determines how many bytes are sent at a time.
    address (list): contains ip address (group) and port number in form [IP, port].
    ttl (int): Time that a datagram has to live in the network.
    '''
    def __init__(self, chunk_size, address, ttl):
        '''Constructor for SendSpecData class.
        
        Parameters
        ----------
        chunk_size: <int>
            Determines how many bytes are sent at a time.
        address: <list>
            contains ip address (group) and port number in form [IP, port].
        ttl: <int>
            Time that a datagram has to live in the network.
        '''
        SpecInfo.__init__(self)
        self.chunk_size = chunk_size
        self.address = address
        self.ttl = ttl
        self.spec = b""
        self.shape = ()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # Setting socket to be able to send data
    def set_socket_send(self):
        '''Sets socket option for sending data.'''
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.ttl)
        
    def get_data(self):
        '''Gets spectrum data from SpecInfo class.
        
        Returns
        -------
        spec: <bytes>
            Spectrum in bytes.
        '''
        SpecInfo.get_spec(self)
        self.spec = SpecInfo.get_spec_compressed(self)
        self.shape = list(SpecInfo.get_shape(self))
        return self.spec

    def send_data(self, client_address):
        '''Sends the compressed spectrum data, an empty bytes string, and the shape of the original np array.
        
        An empty bytes string is sent over to the client so the client knows when to stop receiving data.

        Parameters
        ----------
        client_address: <tuple>
            Address of the client from which the data came from.
        '''
        # Sending over spectrum data by chunk
        b = b""
        i = 0
        for i in range(math.ceil(len(self.spec) / self.chunk_size)):
            b = self.spec[i * self.chunk_size:(i + 1) * self.chunk_size]
            self.sock.sendto(b, client_address)
            
        print("Data has been sent.")    

        # Sending over 0 bytes so recv loop knows when to stop
        b0 = b""
        self.sock.sendto(b0, client_address)

        # Sending over shape for reshaping
        self.sock.sendto(b"%a" % self.shape, client_address)

        #self.sock.close()