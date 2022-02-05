from server import SendSpecData, ReceiveSettings
import json

# Server class parameters
ip = '127.0.0.1'
port = 5004
server_address = (ip, port)
ttl = 2
chunk_size = 500

# Initializing SendSpecData and ReceiveSettings classes
s = SendSpecData(chunk_size, server_address, ttl)
r = ReceiveSettings()
while True:
    
    # Setting up address and socket, which is then set to receive
    r.set_server_address(server_address)
    r.set_sock()
    r.set_socket_receive()

    # Receiving data and deciding what to do with it
    received_data = r.receive_settings()
    if len(received_data[0]) == 0:
        client_address = received_data[1]
    else:
        settings = json.loads(received_data[0])
        client_address = received_data[1]

    # Settings for spectrometer
    trig_val = settings[0]
    int_time_micros = settings[1]

    # Initializing Server methods
    s.setup_spec(trig_val, int_time_micros)
    s.set_socket_send()
    s.get_data()

    s.send_data(client_address)
