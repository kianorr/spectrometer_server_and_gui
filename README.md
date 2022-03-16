# UDP Multicast Server for OceanInsight Spectrometer
UDP multicast server for sending spectrometer data. Spectrometer settings can be set from client side.

![image](https://user-images.githubusercontent.com/60586957/152635600-66e31da5-2bba-4239-b36f-e73af1b37fea.png)


## Instructions
1. Run main_server.py to receive parameters.
2. Run main_client.py and press "Start Animation" to start and send over parameters.
- or alternatively, run main_client_no_gui.py

### A Couple Warnings
1. `matplotlib` is slow and say for 16 $\mu$s shot with 4 $\mu$s integration time, there might only be two spectrums collected. Planning on fixing it but haven't gotten the chance.
2. File names might write over each other if the client is closed and restarted.
