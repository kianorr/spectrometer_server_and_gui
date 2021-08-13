# SENDER

import socket
import struct
import json
import math
import numpy as np
from specDataClass import SpecInfo

# Receives parameters for spectrometer settings from client
class ReceiveParameters:
    def __init__(self, address):
        self.address = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # Setting up for receiving
    def sockets_Receive(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.address[1]))
        mreq = struct.pack("4sl", socket.inet_aton(self.address[0]), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    # Received in bytes then converted
    def receiveParameters(self):
        bSpecInfo_parameters = self.sock.recv(4096)
        SpecInfo_parameters = json.loads(bSpecInfo_parameters)
        return SpecInfo_parameters

# Sends spectrometer data to client
class Server(SpecInfo):
    def __init__(self, chunkSize, address, ttl, trigVal, intTime, deviceNum):
        SpecInfo.__init__(self, trigVal, intTime, deviceNum)
        SpecInfo.getSpec(self)
        self.chunkSize = chunkSize
        self.address = address
        self.ttl = ttl
        self.spectrum = b""
        self.shape = ()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # Setting socket to be able to send data
    def sockets_Send(self):
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.ttl)
        
    def getData(self):
        self.spectrum = SpecInfo.getSpecCompressed(self)
        self.shape = list(SpecInfo.getShape(self))
        return self.spectrum

    def sendData(self):
        # Sending over spectrum data by chunk
        b = b""
        i = 0
        for i in range(math.ceil(len(self.spectrum) / self.chunkSize)):
            b = self.spectrum[i * self.chunkSize:(i + 1) * self.chunkSize]
            self.sock.sendto(b, (self.address[0], self.address[1]))
            
        # Sending over 0 bytes so recv loop knows when to stop
        b0 = b""
        self.sock.sendto(b0, (self.address[0], self.address[1]))

        # Sending over shape for reshaping
        self.sock.sendto(b"%a" % self.shape, (self.address[0], self.address[1]))
        
        self.sock.close()

# Server class parameters
group = '224.1.1.1'
port = 5004
address = [group, port]
ttl = 2
chunkSize = 10

# Initializing ReceiveParameters methods
p = ReceiveParameters(address)
p.sockets_Receive()
params = p.receiveParameters()

# SpecInfo class parameters
# From client.py, SpecInfo_parameters = [trigVal, intTime, deviceNum]
trigVal = params[0]
intTime = params[1]
deviceNum = params[2]

# Initializing Server methods
s = Server(chunkSize, address, ttl, trigVal, intTime, deviceNum)
s.sockets_Send()
s.getData()
s.sendData()