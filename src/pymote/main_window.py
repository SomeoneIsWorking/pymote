"""
Main application window
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QGroupBox
)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont, QColor

from .core import WiimoteReader, enumerate_wiimotes
from .widgets import IRDisplay, ButtonDisplay, OrientationDisplay


class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.reader = WiimoteReader()
        self.init_ui()
        
        # Setup update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(100)
        
        # Connect reader signal
        self.reader.data_updated.connect(self.on_data_updated)
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("DolphinBar Wiimote Viewer")
        self.setGeometry(100, 100, 1000, 700)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Connection controls
        conn_group = QGroupBox("Connection")
        conn_layout = QHBoxLayout()
        
        self.device_combo = QComboBox()
        self.refresh_devices()
        conn_layout.addWidget(QLabel("Device:"))
        conn_layout.addWidget(self.device_combo, 1)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        conn_layout.addWidget(self.connect_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_devices)
        conn_layout.addWidget(refresh_btn)
        
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # Main display area
        display_layout = QHBoxLayout()
        
        # Left column: IR and Buttons
        left_layout = QVBoxLayout()
        
        ir_group = QGroupBox("IR Camera View")
        ir_layout = QVBoxLayout()
        self.ir_display = IRDisplay()
        ir_layout.addWidget(self.ir_display)
        ir_group.setLayout(ir_layout)
        left_layout.addWidget(ir_group)
        
        btn_group = QGroupBox("Buttons")
        btn_layout = QVBoxLayout()
        self.button_display = ButtonDisplay()
        btn_layout.addWidget(self.button_display)
        btn_group.setLayout(btn_layout)
        left_layout.addWidget(btn_group)
        
        display_layout.addLayout(left_layout, 2)
        
        # Right column: Orientation
        orient_group = QGroupBox("Orientation (Accelerometer)")
        orient_layout = QVBoxLayout()
        self.orientation_display = OrientationDisplay()
        orient_layout.addWidget(self.orientation_display)
        
        self.accel_label = QLabel("Accel: X=0 Y=0 Z=0")
        self.accel_label.setFont(QFont("Monospace", 10))
        orient_layout.addWidget(self.accel_label)
        
        orient_group.setLayout(orient_layout)
        display_layout.addWidget(orient_group, 1)
        
        layout.addLayout(display_layout)
        
        # Status bar
        self.status_label = QLabel("Not connected")
        layout.addWidget(self.status_label)
    
    def refresh_devices(self):
        """Refresh list of available devices"""
        self.device_combo.clear()
        
        devices = enumerate_wiimotes()
        for dev in devices:
            path = dev['path']
            product = dev.get('product_string', 'Unknown')
            self.device_combo.addItem(f"{product}", path)
        
        if self.device_combo.count() == 0:
            self.device_combo.addItem("No devices found", None)
    
    def toggle_connection(self):
        """Connect or disconnect from device"""
        if self.reader.data.connected:
            self.reader.stop_reading()
            self.reader.disconnect()
            self.connect_btn.setText("Connect")
            self.status_label.setText("Disconnected")
        else:
            device_path = self.device_combo.currentData()
            if device_path:
                if self.reader.connect(device_path):
                    self.reader.start_reading()
                    self.connect_btn.setText("Disconnect")
                    self.status_label.setText("Connected")
                else:
                    self.status_label.setText("Failed to connect")
    
    def on_data_updated(self, data):
        """Handle updated Wiimote data"""
        self.ir_display.update_ir(data.ir_points)
        self.button_display.update_buttons(data.buttons)
        self.orientation_display.update_orientation(data.accel_x, data.accel_y, data.accel_z)
        self.accel_label.setText(f"Accel: X={data.accel_x} Y={data.accel_y} Z={data.accel_z}")
    
    def update_status(self):
        """Update status display"""
        if self.reader.data.connected:
            self.status_label.setStyleSheet("color: #00ff00")
        else:
            self.status_label.setStyleSheet("color: #ff0000")
    
    def closeEvent(self, event):
        """Handle window close"""
        self.reader.stop_reading()
        self.reader.disconnect()
        event.accept()
