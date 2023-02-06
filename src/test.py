import ctypes
import numpy.ctypeslib as ctl
from numpy.ctypeslib import ndpointer
import numpy as np

class BLE_Sensor:
    def __init__(self, name):
        self.name = name
        self.gatt_data = {
        "value_char": None,
        "name_descriptor": None,
        "unit_descriptor": None,
        "warmup1_descritpor": None,
        "warmup2_descriptor": None,
        "activation_descriptor": None,
        }
        self.sensor_values = {"raw": None, "name": None, "unit": None, "warmup1": None, "warmup2": None, "activated": None}
        



if __name__=="__main__":
    lib = ctypes.cdll.LoadLibrary("./toFloat.so")
    ctoFloat = lib.toFloat
    ctoFloat.restype = None
    ctoFloat.argtypes = [ctl.ndpointer(np.uint8, flags='aligned, c_contiguous')]
    pyvals = np.array([[0x1,0x2, 0x41, 0x3]], dtype=np.uint8)
    
    ctoFloat(pyvals)
    
    



