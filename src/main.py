import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from gui import RLMainWindow
from util import RLManager

style = """
/* --- Main Window --- */
QMainWindow {
    background-color: #1e1e2f;
    font-family: "Segoe UI", sans-serif;
}

/* --- Tabs --- */
QTabWidget::pane {
    border: 1px solid #444;
    border-radius: 6px;
    padding: 8px;
    background-color: #272734;
}

QTabBar::tab {
    background: #2e2e3f;
    color: #ccc;
    padding: 10px 18px;
    border-radius: 6px;
    margin: 2px;
}

QTabBar::tab:selected {
    background: #4e5d6c;
    color: white;
    border-bottom: 2px solid #3a4b63;
}

/* --- Buttons --- */
QPushButton {
    background-color: #4e5d6c;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #6c7d8c;
}

QPushButton:disabled {
    background-color: #3a4460;
    color: #888;
}

/* --- Labels --- */
QLabel {
    color: #ffffff;
    font-size: 14px;
}

QLabel.info {
    color: #bfbfcf;
    font-size: 12px;
}

QLabel.subtitle {
    color: #cfcfe6;
    font-size: 13px;
}

/* --- Status Labels --- */
QLabel.status {
    border-radius: 8px;
    padding: 6px 12px;
    font-weight: 600;
}

/* Status states */
QLabel.status[status="ready"] {
    background-color: #dff7e0;
    color: #2ca84a;
}

QLabel.status[status="warning"] {
    background-color: #fff6e0;
    color: #b77b00;
}

QLabel.status[status="error"] {
    background-color: #ffe6e6;
    color: #d02a2a;
}

QLabel.status[status="incomplete"] {
    background-color: #ededf5;
    color: #7a7aa8;
}

/* --- Cards --- */
QFrame#card {
    background: qlineargradient(x1:0 y1:0, x2:0 y2:1,
                                stop:0 #2b2b3f, stop:1 #232332);
    border-radius: 10px;
    padding: 12px;
}

QFrame#card QLabel {
    color: #c9c9d3;
}

/* --- Specific tab overrides --- */
/* Set Up tab: softer background for better contrast with status */
QWidget#setup_tab {
    background-color: #2a2a3f;
}

QWidget#setup_tab QLabel {
    color: #e0e0f0;
}

/* Home tab: keeps darker, strong look */
QWidget#home_tab {
    background-color: #1e1e2f;
}

QWidget#home_tab QLabel#welcome {
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
}

QWidget#home_tab QLabel#subtitle {
    font-size: 13px;
    color: #cfcfe6;
}

/* ScrollArea: remove border and background to blend nicely */
QScrollArea {
    border: none;
    background: transparent;
}
"""


def main():
    rl_manager = RLManager()
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion")  

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 47))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(39, 39, 52))
    palette.setColor(QPalette.AlternateBase, QColor(46, 46, 63))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(78, 93, 108))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(108, 125, 140))
    palette.setColor(QPalette.Highlight, QColor(78, 93, 108))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    app.setStyleSheet(style)

    window = RLMainWindow(rl_manager)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()