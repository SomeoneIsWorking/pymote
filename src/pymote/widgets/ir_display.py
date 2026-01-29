"""
IR Camera display widget
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont

from ..constants import IR_CAMERA_RES_X, IR_CAMERA_RES_Y


class IRDisplay(QWidget):
    """Widget to display IR camera view"""
    def __init__(self):
        super().__init__()
        self.ir_points = []
        self.setMinimumSize(400, 300)
        
    def update_ir(self, points):
        """Update IR points"""
        self.ir_points = points
        self.update()
    
    def paintEvent(self, event):
        """Draw IR points"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(20, 20, 30))
        
        # Draw grid
        painter.setPen(QPen(QColor(50, 50, 60), 1))
        for i in range(0, self.width(), 50):
            painter.drawLine(i, 0, i, self.height())
        for i in range(0, self.height(), 50):
            painter.drawLine(0, i, self.width(), i)
        
        # Draw crosshair at center
        painter.setPen(QPen(QColor(100, 100, 120), 1, Qt.PenStyle.DashLine))
        painter.drawLine(self.width() // 2, 0, self.width() // 2, self.height())
        painter.drawLine(0, self.height() // 2, self.width(), self.height() // 2)
        
        # Draw IR points
        scale_x = self.width() / IR_CAMERA_RES_X
        scale_y = self.height() / IR_CAMERA_RES_Y
        
        for x, y, size in self.ir_points:
            # Convert to widget coordinates
            wx = int(x * scale_x)
            wy = int(y * scale_y)
            
            # Draw point with size
            radius = max(5, size * 2)
            
            # Glow effect
            for r in range(radius + 10, radius, -2):
                alpha = int(100 * (1 - (r - radius) / 10))
                painter.setBrush(QBrush(QColor(255, 100, 100, alpha)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(wx - r, wy - r, r * 2, r * 2)
            
            # Main point
            painter.setBrush(QBrush(QColor(255, 50, 50)))
            painter.setPen(QPen(QColor(255, 200, 200), 2))
            painter.drawEllipse(wx - radius, wy - radius, radius * 2, radius * 2)
            
            # Crosshair on point
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawLine(wx - radius - 5, wy, wx + radius + 5, wy)
            painter.drawLine(wx, wy - radius - 5, wx, wy + radius + 5)
        
        # Draw info text
        painter.setPen(QColor(200, 200, 200))
        painter.setFont(QFont("Monospace", 10))
        painter.drawText(10, 20, f"IR Points: {len(self.ir_points)}")
