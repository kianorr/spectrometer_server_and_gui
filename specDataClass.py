from seabreeze.spectrometers import Spectrometer, list_devices
import zlib
import numpy as np

class SpecInfo(Spectrometer):
    def __init__(self, trigVal, intTime, deviceNum):
        device = list_devices()[deviceNum]
        Spectrometer.__init__(self, device)
        self.spectrometer = Spectrometer(device)
        self.spectrumData = np.array([[]])
        self.trigVal = trigVal
        self.intTime = intTime
    
    # Sets the trigger mode, which are as follows:
    # normal = 0
    # level/software = 1
    # synchronization = 2
    # edge/hardware = 3
    def setTriggerMode(self):
        spec = self.spectrometer
        spec.trigger_mode(self.trigVal)
    
    # Sets integration time in microseconds
    def setIntTime(self):
        self.spectrometer.integration_time_micros(self.intTime)
    
    # Gets spectrometer data using seabreeze's spectrum() function
    def getSpec(self):
        spec = self.spectrometer
        self.spectrumData = spec.spectrum()
        return self.spectrumData
        
    def getShape(self):
        shape = self.spectrumData.shape
        return shape
    
    # Compresses spectrometer data for easy sending
    def getSpecCompressed(self):
        self.specCompressed = zlib.compress(self.spectrumData.tobytes())
        return self.specCompressed