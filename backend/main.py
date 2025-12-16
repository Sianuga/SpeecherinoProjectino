#!/usr/bin/env python3
"""
Rubber Duck Assistant - Asystent głosowy dla programistów
Inspirowany metodą "gumowej kaczuszki" (Rubber Duck Debugging)
"""

import sys
import os

# Dodaj ścieżkę do modułów
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.app_controller import AppController


def main():
    # Ustawienia dla high DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Rubber Duck Assistant")
    app.setOrganizationName("RubberDuck")
    app.setQuitOnLastWindowClosed(False)  # Nie zamykaj gdy okno jest ukryte
    
    # Styl aplikacji
    app.setStyleSheet("""
        QMainWindow, QDialog {
            background-color: #fafafa;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-top: 12px;
            padding: 15px;
            padding-top: 25px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 5px;
        }
        QPushButton {
            background-color: #fff;
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #f5f5f5;
            border-color: #ccc;
        }
        QPushButton:pressed {
            background-color: #eee;
        }
        QLineEdit, QTextEdit {
            border: 1px solid #ddd;
            border-radius: 6px;
            padding: 8px;
            background-color: #fff;
        }
        QLineEdit:focus, QTextEdit:focus {
            border-color: #4CAF50;
        }
        QListWidget {
            border: 1px solid #ddd;
            border-radius: 6px;
            background-color: #fff;
        }
        QListWidget::item {
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        QListWidget::item:selected {
            background-color: #e8f5e9;
            color: #2e7d32;
        }
        QListWidget::item:hover {
            background-color: #f5f5f5;
        }
        QTabWidget::pane {
            border: 1px solid #ddd;
            border-radius: 6px;
            background-color: #fff;
        }
        QTabBar::tab {
            padding: 10px 20px;
            border: 1px solid #ddd;
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            background-color: #f5f5f5;
        }
        QTabBar::tab:selected {
            background-color: #fff;
        }
    """)
    
    # Inicjalizacja kontrolera
    controller = AppController()
    controller.initialize()
    controller.show()
    
    # Cleanup przy zamknięciu
    app.aboutToQuit.connect(controller.cleanup)
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
