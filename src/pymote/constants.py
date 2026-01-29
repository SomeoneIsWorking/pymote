"""
DolphinBar Wiimote GUI - Constants and Configuration
"""

# Wiimote button masks (from Dolphin source)
BUTTON_LEFT = 0x0001
BUTTON_RIGHT = 0x0002
BUTTON_DOWN = 0x0004
BUTTON_UP = 0x0008
BUTTON_PLUS = 0x0010
BUTTON_TWO = 0x0100
BUTTON_ONE = 0x0200
BUTTON_B = 0x0400
BUTTON_A = 0x0800
BUTTON_MINUS = 0x1000
BUTTON_HOME = 0x8000

# DolphinBar/Mayflash Wiimote PC Adapter
VENDOR_ID = 0x057e  # Nintendo
PRODUCT_ID = 0x0306  # Wii Remote

# IR Camera specifications
IR_CAMERA_RES_X = 1024
IR_CAMERA_RES_Y = 768

# Accelerometer calibration (8-bit values in report 0x37)
ACCEL_CENTER = 128  # Center point for 8-bit accelerometer data
ACCEL_1G = 25.0  # Approximately 25-30 units = 1G in 8-bit mode

# Report IDs
REPORT_CORE_BUTTONS = 0x30
REPORT_CORE_ACCEL = 0x31
REPORT_CORE_ACCEL_IR12 = 0x33
REPORT_CORE_ACCEL_IR10 = 0x37
