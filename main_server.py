from server import Server, ReceiveParameters

# Server class parameters
group = '224.1.1.1'
port = 5004
address = [group, port]
ttl = 2
chunk_size = 10

# Initializing ReceiveParameters methods
p = ReceiveParameters(address)
p.set_socket_receive()
params = p.receive_parameters()

# SpecInfo class parameters
# From client.py, SpecInfo_parameters = [trigVal, intTime, deviceNum]
trig_val = params[0]
int_time = params[1]
device_num = params[2]

# Initializing Server methods
s = Server(chunk_size, address, ttl, trig_val, int_time, device_num)
s.set_socket_send()
s.get_data()
s.send_data()
