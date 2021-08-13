import socket
import struct
import zlib
import json
import numpy as np

# Sends parameters for spectrometer from client
class SendParameters:
    def __init__(self, address, trigVal, intTime, deviceNum):
        self.address = address
        self.trigVal = trigVal
        self.intTime = intTime
        self.deviceNum = deviceNum
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # Sending chosen spectrometer settings to server side
    def sendParams(self):
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        SpecInfo_parameters = [self.trigVal, self.intTime, self.deviceNum]
        self.sock.sendto(b"%a" % SpecInfo_parameters, (self.address[0], self.address[1]))
        
# Receives spectrometer data
class Receive:
    def __init__(self, address):
        self.bSpectrum = b""
        self.bShape = b""
        self.address = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    
    # Setting socket to receive data
    def sockets_Receive(self):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.address[1]))
        mreq = struct.pack("4sl", socket.inet_aton(self.address[0]), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    # receives spectrum data in form of bytes,
    # then receives 0 bytes to break from loop,
    # and finally it receives data about the shape of the spectrum array.
    def receiveData(self):
        tf = True
        z = b""
        while tf == True:
            z = self.sock.recv(4096)
            self.bSpectrum += z
            if len(z) == 0:
                tf = False

        # receives shape data
        self.bShape = self.sock.recv(1024)

        self.sock.close()

        print("The data has been received.")
    
    # Converts spectrum data and shape from bytes to their original type
    # Sometimes, some bytes are lost but it's very minimal
    def prepareData(self):
        specDecompressed = zlib.decompress(self.bSpectrum)
        shape = tuple(json.loads(self.bShape))
        s = np.frombuffer(specDecompressed).reshape(shape)
        return s
