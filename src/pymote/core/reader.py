"""
Wiimote HID reader and report parser
"""

import struct
import threading
import time
import hid
from PySide6.QtCore import QObject, Signal

from ..constants import VENDOR_ID, PRODUCT_ID
from .models import WiimoteData


class WiimoteReader(QObject):
    """Background thread for reading Wiimote data"""
    data_updated = Signal(object)
    
    def __init__(self):
        super().__init__()
        self.device = None
        self.running = False
        self.data = WiimoteData()
        self.debug = False  # Disable debug output by default
        
    def connect(self, device_path):
        """Connect to a specific Wiimote device"""
        try:
            if self.device:
                self.device.close()
            
            self.device = hid.device()
            self.device.open_path(device_path)
            self.device.set_nonblocking(True)
            self.data.connected = True
            
            # Initialize Wiimote to send accelerometer and IR data
            self._initialize_wiimote()
            
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.data.connected = False
            return False
    
    def _initialize_wiimote(self):
        """Send initialization commands to enable IR and accelerometer"""
        try:
            # Small delay to ensure connection is stable
            time.sleep(0.1)
            
            # Report 0x13: IR Camera Enable (send twice as per Wiimote protocol)
            # Format: [report_id, rumble bit]
            self.device.write([0x13, 0x04])  # Enable IR camera
            time.sleep(0.05)
            self.device.write([0x13, 0x04])  # Enable IR camera (again)
            time.sleep(0.05)
            
            # Report 0x1a: IR Camera Enable 2
            self.device.write([0x1a, 0x04])  # Enable IR camera mode 2
            time.sleep(0.05)
            
            # Write to register 0xb00030 to enable IR camera
            # Report 0x16: Write to Wiimote memory/registers
            # Format: [0x16, flags, address_hi, address_mid, address_lo, size, data...]
            self.device.write([0x16, 0x04, 0xb0, 0x00, 0x30, 0x01, 0x08])
            time.sleep(0.05)
            
            # Write IR sensitivity block 1 (Wii Level 5)
            # 00 00 00 00 00 00 90 00 41
            self.device.write([0x16, 0x04, 0xb0, 0x00, 0x00, 0x09, 
                             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x90, 0x00, 0x41])
            time.sleep(0.05)
            
            # Write IR sensitivity block 2 (Wii Level 5)
            # 40 00
            self.device.write([0x16, 0x04, 0xb0, 0x00, 0x1a, 0x02, 0x40, 0x00])
            time.sleep(0.05)
            
            # Write IR mode (0x01 = basic, 0x03 = extended, 0x05 = full)
            self.device.write([0x16, 0x04, 0xb0, 0x00, 0x33, 0x01, 0x03])  # Set to Extended Mode (3)
            time.sleep(0.05)
            
            # Report 0x12: Set data reporting mode
            # Mode 0x33 = Core Buttons + Accelerometer + IR (12 bytes, Extended)
            # Format: [0x12, continuous | rumble, mode]
            self.device.write([0x12, 0x00, 0x33])  # Set to mode 0x33
            time.sleep(0.05)
            
            print("Wiimote initialized: IR (Extended) and accelerometer enabled")
            
        except Exception as e:
            print(f"Error initializing Wiimote: {e}")
    
    def disconnect(self):
        """Disconnect from Wiimote"""
        self.running = False
        if self.device:
            try:
                self.device.close()
            except:
                pass
            self.device = None
        self.data.connected = False
    
    def parse_report(self, data):
        """Parse Wiimote input report"""
        if not data or len(data) < 2:
            return
        
        report_id = data[0]
        
        # Debug: print report info occasionally
        if self.debug and hasattr(self, '_debug_counter'):
            self._debug_counter += 1
            if self._debug_counter % 50 == 0:  # More frequent debug
                # Show raw data for relevant bytes
                hex_data = ' '.join(f'{b:02x}' for b in data[:20])
                print(f"Report 0x{report_id:02x}, len={len(data)}, data={hex_data}")
        elif self.debug:
            self._debug_counter = 0
            
        # Parse buttons manually to handle the interleaved accelerometer bits
        # Byte 1: Left, Right, Down, Up, Plus, AccelLSB(2), Unknown
        # Byte 2: Two, One, B, A, Minus, AccelLSB, AccelLSB, Home
        if len(data) >= 3:
            b1 = data[1]
            b2 = data[2]
            
            # Reconstruct buttons based on constants.py values:
            # BUTTON_LEFT = 0x0001
            # BUTTON_RIGHT = 0x0002
            # BUTTON_DOWN = 0x0004
            # BUTTON_UP = 0x0008
            # BUTTON_PLUS = 0x0010
            # BUTTON_TWO = 0x0100
            # BUTTON_ONE = 0x0200
            # BUTTON_B = 0x0400
            # BUTTON_A = 0x0800
            # BUTTON_MINUS = 0x1000
            # BUTTON_HOME = 0x8000
            
            buttons = 0
            if b1 & 0x01: buttons |= 0x0001  # Left
            if b1 & 0x02: buttons |= 0x0002  # Right
            if b1 & 0x04: buttons |= 0x0004  # Down
            if b1 & 0x08: buttons |= 0x0008  # Up
            if b1 & 0x10: buttons |= 0x0010  # Plus
            
            if b2 & 0x01: buttons |= 0x0100  # Two
            if b2 & 0x02: buttons |= 0x0200  # One
            if b2 & 0x04: buttons |= 0x0400  # B
            if b2 & 0x08: buttons |= 0x0800  # A
            if b2 & 0x10: buttons |= 0x1000  # Minus
            if b2 & 0x80: buttons |= 0x8000  # Home
            
            self.data.buttons = buttons
        
        # Report 0x30: Core Buttons only
        if report_id == 0x30:
            pass  # Buttons already parsed
        
        # Report 0x31: Core Buttons and Accelerometer
        elif report_id == 0x31 and len(data) >= 6:
            self.data.accel_x = data[3]
            self.data.accel_y = data[4]
            self.data.accel_z = data[5]
        
        # Report 0x33: Core Buttons, Accelerometer and IR (12 bytes)
        elif report_id == 0x33 and len(data) >= 18:
            self.data.accel_x = data[3]
            self.data.accel_y = data[4]
            self.data.accel_z = data[5]
            
            # Parse IR data (Extended mode - 4 objects, 3 bytes each)
            ir_points = []
            for i in range(4):  # Up to 4 IR points
                offset = 6 + i * 3
                if offset + 2 < len(data):
                    x_low = data[offset]
                    y_low = data[offset + 1]
                    xy_high = data[offset + 2]
                    
                    x = x_low | ((xy_high & 0x30) << 4)
                    y = y_low | ((xy_high & 0xC0) << 2)
                    size = xy_high & 0x0F
                    
                    # 0x3FF (1023) means not visible
                    if x < 1023 and y < 1023:
                        ir_points.append((x, y, size))
            
            self.data.ir_points = ir_points
        
        # Report 0x37: Core Buttons, Accelerometer and IR (10 bytes) + Extension (6 bytes)
        # ReportCoreAccelIR10Ext6 - IR data is 10 bytes (2 IRBasic structs)
        elif report_id == 0x37 and len(data) >= 19:
            self.data.accel_x = data[3]
            self.data.accel_y = data[4]
            self.data.accel_z = data[5]
            
            # IR Basic mode - 10 bytes total for up to 4 objects (2 IRBasic structs)
            # Each IRBasic is 5 bytes and contains 2 objects
            ir_points = []
            
            # First IRBasic struct (bytes 6-10): objects 1 and 2
            if len(data) >= 11:
                x1 = data[6]
                y1 = data[7]
                xy_bits = data[8]  # Contains high bits for both objects
                x2 = data[9]
                y2 = data[10]
                
                # Extract high bits from byte 8
                # Bit layout: [y1hi:2][x1hi:2][y2hi:2][x2hi:2]
                x1_hi = (xy_bits >> 4) & 0x03
                y1_hi = (xy_bits >> 6) & 0x03
                x2_hi = (xy_bits >> 0) & 0x03
                y2_hi = (xy_bits >> 2) & 0x03
                
                x1_full = (x1_hi << 8) | x1
                y1_full = (y1_hi << 8) | y1
                x2_full = (x2_hi << 8) | x2
                y2_full = (y2_hi << 8) | y2
                
                # 0x3FF (1023) means not visible
                if x1_full < 1023 and y1_full < 1023:
                    ir_points.append((x1_full, y1_full, 5))
                if x2_full < 1023 and y2_full < 1023:
                    ir_points.append((x2_full, y2_full, 5))
            
            # Second IRBasic struct (bytes 11-15): objects 3 and 4
            if len(data) >= 16:
                x3 = data[11]
                y3 = data[12]
                xy_bits2 = data[13]
                x4 = data[14]
                y4 = data[15]
                
                x3_hi = (xy_bits2 >> 4) & 0x03
                y3_hi = (xy_bits2 >> 6) & 0x03
                x4_hi = (xy_bits2 >> 0) & 0x03
                y4_hi = (xy_bits2 >> 2) & 0x03
                
                x3_full = (x3_hi << 8) | x3
                y3_full = (y3_hi << 8) | y3
                x4_full = (x4_hi << 8) | x4
                y4_full = (y4_hi << 8) | y4
                
                if x3_full < 1023 and y3_full < 1023:
                    ir_points.append((x3_full, y3_full, 5))
                if x4_full < 1023 and y4_full < 1023:
                    ir_points.append((x4_full, y4_full, 5))
            
            self.data.ir_points = ir_points
        
        # Report 0x3d: Core Buttons + Accelerometer + IR (36 bytes) - Extension mode
        elif report_id == 0x3d and len(data) >= 21:
            self.data.accel_x = data[3]
            self.data.accel_y = data[4]
            self.data.accel_z = data[5]
            
            # IR data similar to 0x33
            ir_points = []
            for i in range(4):
                offset = 6 + i * 3
                if offset + 2 < len(data):
                    x_low = data[offset]
                    y_low = data[offset + 1]
                    xy_high = data[offset + 2]
                    
                    x = x_low | ((xy_high & 0x30) << 4)
                    y = y_low | ((xy_high & 0xC0) << 2)
                    size = xy_high & 0x0F
                    
                    if x < 1023 and y < 1023:
                        ir_points.append((x, y, size))
            
            self.data.ir_points = ir_points
    
    def read_loop(self):
        """Main reading loop"""
        while self.running:
            if not self.device:
                time.sleep(0.1)
                continue
            
            try:
                data = self.device.read(32, timeout_ms=10)
                if data:
                    self.parse_report(data)
                    self.data_updated.emit(self.data)
            except Exception as e:
                print(f"Read error: {e}")
                time.sleep(0.1)
    
    def start_reading(self):
        """Start the reading thread"""
        if not self.running:
            self.running = True
            thread = threading.Thread(target=self.read_loop, daemon=True)
            thread.start()
    
    def stop_reading(self):
        """Stop the reading thread"""
        self.running = False


def enumerate_wiimotes():
    """Enumerate all connected Wiimote devices"""
    try:
        return hid.enumerate(VENDOR_ID, PRODUCT_ID)
    except Exception as e:
        print(f"Error enumerating devices: {e}")
        return []
