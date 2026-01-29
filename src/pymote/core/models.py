"""
Wiimote data structures and models
"""

class WiimoteData:
    """Container for Wiimote state"""
    def __init__(self):
        self.buttons = 0
        self.accel_x = 512
        self.accel_y = 512
        self.accel_z = 512
        self.ir_points = []  # List of (x, y, size) tuples
        self.battery = 0
        self.connected = False
        
    def __repr__(self):
        return (f"WiimoteData(buttons=0x{self.buttons:04x}, "
                f"accel=({self.accel_x}, {self.accel_y}, {self.accel_z}), "
                f"ir_points={len(self.ir_points)}, connected={self.connected})")
