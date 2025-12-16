#!/usr/bin/env python3
"""
Rubber Duck Assistant - Asystent głosowy dla programistów
Inspirowany metodą "gumowej kaczuszki" (Rubber Duck Debugging)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.app_controller import AppController


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Rubber Duck Assistant")
    app.setOrganizationName("RubberDuck")
    app.setQuitOnLastWindowClosed(False)
    
    # Poprawiony styl z lepszą widocznością kolorów
    app.setStyleSheet("""
        QMainWindow, QDialog {
            background-color: #2b2b2b;
            color: #e0e0e0;
        }
        QWidget {
            color: #e0e0e0;
        }
        QLabel {
            color: #e0e0e0;
            font-size: 13px;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #4a4a4a;
            border-radius: 8px;
            margin-top: 12px;
            padding: 15px;
            padding-top: 25px;
            background-color: #333333;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 8px;
            color: #ffd54f;
            font-size: 14px;
        }
        QPushButton {
            background-color: #424242;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
            color: #ffffff;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
            border-color: #ffd54f;
        }
        QPushButton:pressed {
            background-color: #555555;
        }
        QLineEdit, QTextEdit {
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 8px;
            background-color: #3a3a3a;
            color: #ffffff;
            font-size: 13px;
        }
        QLineEdit:focus, QTextEdit:focus {
            border-color: #ffd54f;
        }
        QLineEdit::placeholder {
            color: #888888;
        }
        QListWidget {
            border: 1px solid #555555;
            border-radius: 6px;
            background-color: #3a3a3a;
            color: #e0e0e0;
        }
        QListWidget::item {
            padding: 10px;
            border-bottom: 1px solid #4a4a4a;
            color: #e0e0e0;
        }
        QListWidget::item:selected {
            background-color: #4a6a4a;
            color: #ffffff;
        }
        QListWidget::item:hover {
            background-color: #454545;
        }
        QTabWidget::pane {
            border: 1px solid #555555;
            border-radius: 6px;
            background-color: #333333;
        }
        QTabBar::tab {
            padding: 10px 20px;
            border: 1px solid #555555;
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            background-color: #3a3a3a;
            color: #b0b0b0;
        }
        QTabBar::tab:selected {
            background-color: #333333;
            color: #ffd54f;
        }
        QTabBar::tab:hover {
            color: #ffffff;
        }
        QComboBox {
            background-color: #3a3a3a;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 8px;
            color: #ffffff;
        }
        QComboBox:hover {
            border-color: #ffd54f;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox QAbstractItemView {
            background-color: #3a3a3a;
            color: #ffffff;
            selection-background-color: #4a6a4a;
        }
        QSpinBox {
            background-color: #3a3a3a;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 8px;
            color: #ffffff;
        }
        QSpinBox:focus {
            border-color: #ffd54f;
        }
        QCheckBox {
            color: #e0e0e0;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 1px solid #555555;
            background-color: #3a3a3a;
        }
        QCheckBox::indicator:checked {
            background-color: #ffd54f;
            border-color: #ffd54f;
        }
        QMessageBox {
            background-color: #2b2b2b;
        }
        QMessageBox QLabel {
            color: #e0e0e0;
        }
        QMessageBox QPushButton {
            min-width: 80px;
        }
        QFrame {
            color: #e0e0e0;
        }
        QScrollBar:vertical {
            background-color: #2b2b2b;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #555555;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #666666;
        }
    """)
    
    controller = AppController()
    controller.initialize()
    controller.show()
    
    app.aboutToQuit.connect(controller.cleanup)
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
