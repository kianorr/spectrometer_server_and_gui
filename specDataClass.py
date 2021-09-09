from seabreeze.spectrometers import Spectrometer, list_devices
import zlib
import numpy as np

class SpecInfo(Spectrometer):
    '''Initializes OceanInsight device and obtains spectrum data using python-seabreeze library.
    
    Inherits Spectrometer class from seabreeze.spectrometers.
    '''
    def __init__(self):
        '''Constructor for SpecInfo class.
        
        Initializes Spectrometer class from seabreeze.spectrometers.
        '''
        # Initializing spectrometer device
        device = list_devices()[0]
        Spectrometer.__init__(self, device)
        self.spectrometer = Spectrometer(device)
        
        # Initializing spectrum data
        self.spectrum_data = np.array([[]])

    def setup_spec(self, trig_val, int_time_ms):
        '''Sets trigger mode and integration time.
        
        Parameters
        ----------
        trig_val: <int>
            normal = 0\n
            level/software = 1\n
            synchronization = 2\n
            edge/hardware = 3
        
        int_time_ms: <int>
            Integration time in microseconds.
        '''
        self.spectrometer.trigger_mode(trig_val)
        self.spectrometer.integration_time_micros(int_time_ms)

    # Gets spectrometer data using seabreeze's spectrum() function
    def get_spec(self):
        '''This function obtains data (intensity and wavelength) from the spectrometer.
        
        The data is obtained using seabreeze's spectrum() function.
        
        Returns
        -------
        spectrum_data: <numpy.ndarray>
            2D array that contains wavelengths and intensities.
        '''
        spec = self.spectrometer
        self.spectrum_data = spec.spectrum()
        return self.spectrum_data
        
    def get_shape(self):
        '''Gets the shape of the 2D numpy array for the spectrum.

        Returns
        -------
        shape: <tuple>
        '''
        shape = self.spectrum_data.shape
        return shape
    
    # Compresses spectrometer data for easy sending
    def get_spec_compressed(self):
        '''Compresses spectrum data from getSpec() method for easy sending.

        Returns
        -------
        spec_compressed: <bytes>
            compresses the spectrum using zlib.
        '''
        spec_compressed = zlib.compress(self.spectrum_data.tobytes(), 0)
        return spec_compressed
