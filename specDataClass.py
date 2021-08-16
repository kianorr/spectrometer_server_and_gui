from seabreeze.spectrometers import Spectrometer, list_devices
import zlib
import numpy as np

class SpecInfo(Spectrometer):
    '''
    Initializes OceanInsight device and obtains spectrum data using python-seabreeze library.
    
    Inherits Spectrometer class from seabreeze.
    
    Attributes
    ----------
    trigVal (int): Sets trigger mode. See setTriggerMode() method.
    intTime (int): Integration time in microseconds.
    deviceNum (int): Sets which device you want to use if there are multiple. If there is only one, then choose 0.
    '''
    def __init__(self, trig_val, int_time, device_num):
        '''
        Constructor for SpecInfo class.
        
        Parameters
        ----------
        trigVal (int): Sets trigger mode. See setTriggerMode() method.
        intTime (int): Integration time in microseconds.
        deviceNum (int): Sets which device you want to use if there are multiple. If there is only one, then choose 0.
        '''
        device = list_devices()[device_num]
        Spectrometer.__init__(self, device)
        self.spectrometer = Spectrometer(device)
        self.spectrum_data = np.array([[]])
        self.trig_val = trig_val
        self.int_time = int_time
    
    def __set_trigger_mode(self):
        ''' 
        This function sets the trigger mode.
        
        A specific trigger mode can be set with the following values:
        normal = 0
        level/software = 1
        synchronization = 2
        edge/hardware = 3 
        '''
        spec = self.spectrometer
        spec.trigger_mode(self.trig_val)
    
    # Sets integration time in microseconds
    def __set_int_time(self):
        '''
        This function sets the integration time in microseconds.
        '''
        spec = self.spectrometer
        spec.integration_time_micros(self.int_time)
    
    # Gets spectrometer data using seabreeze's spectrum() function
    def get_spec(self):
        '''
        This function obtains data (intensity and wavelength) from the spectrometer.
        
        The data is obtained using seabreeze's spectrum() function.
        
        Returns
        -------
        spectrumData: <numpy.ndarray>
            2D array that contains wavelengths and intensities.
        '''
        spec = self.spectrometer
        self.spectrum_data = spec.spectrum()
        return self.spectrum_data
        
    def get_shape(self):
        '''
        Gets the shape of the 2D numpy array for the spectrum.

        Returns
        -------
        shape: <tuple>
        '''
        shape = self.spectrum_data.shape
        return shape
    
    # Compresses spectrometer data for easy sending
    def get_spec_compressed(self):
        '''
        Compresses spectrum data from getSpec() for easy sending.

        Returns
        -------
        specCompressed: <bytes>
        '''
        spec_compressed = zlib.compress(self.spectrum_data.tobytes())
        return spec_compressed
