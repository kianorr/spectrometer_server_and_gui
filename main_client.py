from client import SendParameters, Receive

# Choosing spectrometer settings
trig_val = 0        # value of trigger mode
int_time = 1000     # integration time in microseconds
device_num = 0      # element value for device list (if there's only one device, then it's zero)

# Address parameters
group = '224.1.1.1'
port = 5004
address = [group, port]

# Intitializing SendParameters class
s = SendParameters(address, trig_val, int_time, device_num)
s.send_parameters()

# Initializing Receive class
r = Receive(address)
r.set_socket_receive()
r.receive_data()
print(r.prepare_data())
