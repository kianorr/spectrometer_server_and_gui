from client import SendParameters, Receive

# Choosing spectrometer settings
trigVal = 0        # value of trigger mode
intTime = 1000     # integration time in microseconds
deviceNum = 0      # element value for device list (if there's only one device, then it's zero)

# Address parameters
group = '224.1.1.1'
port = 5004
address = [group, port]

# Intitializing SendParameters class
s = SendParameters(address, trigVal, intTime, deviceNum)
s.sendParams()

# Initializing Receive class
# Not sure if there's a better way to do this
r = Receive(address)
r.sockets_Receive()
r.receiveData()
print(r.prepareData())