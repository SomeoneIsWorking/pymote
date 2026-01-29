"""
DolphinBar Wiimote GUI Application
Shows IR aiming, orientation, and button presses for Wiimote in Mode 4
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from .main_window import MainWindow


def setup_dark_theme(app):
    """Setup dark theme for the application"""
    app.setStyle("Fusion")
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(palette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(palette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(palette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(palette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(palette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(palette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(palette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(palette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(palette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(palette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(palette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(palette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(palette)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    setup_dark_theme(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
