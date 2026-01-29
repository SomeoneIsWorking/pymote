"""
Button state display widget
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont

from ..constants import (
    BUTTON_A, BUTTON_B, BUTTON_ONE, BUTTON_TWO,
    BUTTON_PLUS, BUTTON_MINUS, BUTTON_HOME,
    BUTTON_UP, BUTTON_DOWN, BUTTON_LEFT, BUTTON_RIGHT
)


class ButtonDisplay(QWidget):
    """Widget to display button states"""
    def __init__(self):
        super().__init__()
        self.buttons = 0
        self.setMinimumHeight(200)
        
    def update_buttons(self, buttons):
        """Update button state"""
        self.buttons = buttons
        self.update()
    
    def paintEvent(self, event):
        """Draw buttons"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(30, 30, 40))
        
        # Button layout: (label, mask, x, y, size)
        buttons_layout = [
            ("A", BUTTON_A, 200, 80, 50),
            ("B", BUTTON_B, 200, 140, 40),
            ("1", BUTTON_ONE, 140, 110, 35),
            ("2", BUTTON_TWO, 260, 110, 35),
            ("+", BUTTON_PLUS, 320, 80, 30),
            ("-", BUTTON_MINUS, 80, 80, 30),
            ("HOME", BUTTON_HOME, 200, 50, 40),
            ("↑", BUTTON_UP, 50, 30, 30),
            ("↓", BUTTON_DOWN, 50, 90, 30),
            ("←", BUTTON_LEFT, 20, 60, 30),
            ("→", BUTTON_RIGHT, 80, 60, 30),
        ]
        
        for label, mask, x, y, size in buttons_layout:
            pressed = (self.buttons & mask) != 0
            
            # Button circle
            if pressed:
                painter.setBrush(QBrush(QColor(100, 200, 255)))
                painter.setPen(QPen(QColor(150, 220, 255), 3))
            else:
                painter.setBrush(QBrush(QColor(60, 60, 80)))
                painter.setPen(QPen(QColor(100, 100, 120), 2))
            
            painter.drawEllipse(x - size//2, y - size//2, size, size)
            
            # Button label
            painter.setPen(QColor(255, 255, 255))
            font = QFont("Arial", 10, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(x - size//2, y - size//2, size, size, 
                           Qt.AlignmentFlag.AlignCenter, label)
