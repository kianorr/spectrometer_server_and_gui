from server import SendSpecData, ReceiveSettings
import json

# Server class parameters
group = '127.0.0.1'
port = 5004
server_address = [group, port]
ttl = 2
chunk_size = 500

# Initializing SendSpecData class
s = SendSpecData(chunk_size, server_address, ttl)
while True:

    # Initializing ReceiveSettings class and socket
    r = ReceiveSettings(server_address)
    r.set_socket_receive()

    # Receiving data and deciding what to do with it
    received_data = r.receive_settings()
    if len(received_data[0]) == 0:
        client_address = received_data[1]
    else:
        settings = []
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
