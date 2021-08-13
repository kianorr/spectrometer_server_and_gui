from server import Server, ReceiveParameters

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