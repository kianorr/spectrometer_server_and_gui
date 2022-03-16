from client import ReceiveSpecData, SendSettings
from GUI_client import SaveData
import sys

try:
    # terminal inputs
    server_address = sys.argv[1].split(':')
    int_time_micros = sys.argv[2]
    trig_val = sys.argv[3]

except IndexError:
    print(
    "Terminal args should be ip:port trigger_mode integration_time\n" +
    "For example: 127.0.0.1:5004 4000 0"
    )

r = ReceiveSpecData()
s = SendSettings((server_address[0], int(server_address[1])), int(trig_val), int(int_time_micros))
sd = SaveData(file_number=0)
spec_list = []
try:
    while True:
        # Sending data
        s.send_settings()
        client_port = s.get_port()

        s.send_zero_bytes()
        r.create_socket()

        # Receiving data
        r.set_socket_receive()
        r.bind_socket(client_port, server_address)
        r.receive_data()
        spec = r.prepare_data()
        spec_list.append(spec)

finally:
    sd.save_data(spec)
    print("done")
