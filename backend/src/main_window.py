from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QSystemTrayIcon,
    QMenu, QMessageBox, QApplication, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QAction, QFont, QPixmap, QPainter, QColor

from .dialogs import ProjectDialog, SettingsDialog
from .config_manager import ConfigManager


def create_duck_icon(size=64):
    """Tworzy ikonę kaczki"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Ciało
    painter.setBrush(QColor(255, 213, 79))
    painter.setPen(QColor(200, 160, 50))
    painter.drawEllipse(8, 20, size - 16, size - 28)
    
    # Głowa
    head_size = size // 3
    painter.drawEllipse(size // 2 - head_size // 2, 8, head_size, head_size)
    
    # Dziób
    painter.setBrush(QColor(255, 152, 0))
    painter.drawEllipse(size // 2 + head_size // 4, 14, 12, 8)
    
    # Oko
    painter.setBrush(QColor(0, 0, 0))
    painter.drawEllipse(size // 2 - 2, 14, 5, 5)
    
    painter.end()
    return QIcon(pixmap)


class MainWindow(QMainWindow):
    start_listening = pyqtSignal()
    stop_listening = pyqtSignal()
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.setWindowTitle("🦆 Rubber Duck Assistant")
        self.setMinimumSize(600, 500)
        
        self.setup_ui()
        self.setup_tray()
        self.refresh_projects_list()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("🦆 Rubber Duck Assistant")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        settings_btn = QPushButton("⚙️ Ustawienia")
        settings_btn.clicked.connect(self.open_settings)
        header_layout.addWidget(settings_btn)
        
        layout.addLayout(header_layout)
        
        # Aktywny projekt
        active_group = QGroupBox("Aktywny Projekt")
        active_layout = QVBoxLayout()
        
        self.active_project_label = QLabel("Brak aktywnego projektu")
        self.active_project_label.setFont(QFont("Arial", 12))
        self.active_project_label.setStyleSheet("color: #666;")
        active_layout.addWidget(self.active_project_label)
        
        self.active_project_desc = QLabel("")
        self.active_project_desc.setWordWrap(True)
        self.active_project_desc.setStyleSheet("color: #888; font-size: 11px;")
        active_layout.addWidget(self.active_project_desc)
        
        active_group.setLayout(active_layout)
        layout.addWidget(active_group)
        
        # Lista projektów
        projects_group = QGroupBox("Projekty")
        projects_layout = QVBoxLayout()
        
        self.projects_list = QListWidget()
        self.projects_list.setMinimumHeight(150)
        self.projects_list.itemDoubleClicked.connect(self.activate_project)
        projects_layout.addWidget(self.projects_list)
        
        projects_buttons = QHBoxLayout()
        
        add_btn = QPushButton("➕ Nowy Projekt")
        add_btn.clicked.connect(self.add_project)
        projects_buttons.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ Edytuj")
        edit_btn.clicked.connect(self.edit_project)
        projects_buttons.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Usuń")
        delete_btn.clicked.connect(self.delete_project)
        projects_buttons.addWidget(delete_btn)
        
        activate_btn = QPushButton("✅ Aktywuj")
        activate_btn.clicked.connect(self.activate_selected_project)
        projects_buttons.addWidget(activate_btn)
        
        projects_layout.addLayout(projects_buttons)
        projects_group.setLayout(projects_layout)
        layout.addWidget(projects_group)
        
        # Informacje
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f7ff;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        hotkey = self.config_manager.config.get("push_to_talk_key", "ctrl+shift+d")
        info_label = QLabel(f"💡 Skrót Push-to-Talk: <b>{hotkey}</b>")
        info_label.setStyleSheet("color: #333;")
        info_layout.addWidget(info_label)
        
        info_label2 = QLabel("Kliknij w kaczkę lub użyj skrótu aby rozpocząć rozmowę")
        info_label2.setStyleSheet("color: #666; font-size: 11px;")
        info_layout.addWidget(info_label2)
        
        layout.addWidget(info_frame)
        
        # Przyciski kontrolne
        control_layout = QHBoxLayout()
        control_layout.addStretch()
        
        minimize_btn = QPushButton("Minimalizuj do tray")
        minimize_btn.clicked.connect(self.hide)
        control_layout.addWidget(minimize_btn)
        
        layout.addLayout(control_layout)
    
    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(create_duck_icon())
        self.tray_icon.setToolTip("Rubber Duck Assistant")
        
        tray_menu = QMenu()
        
        show_action = QAction("Pokaż okno", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        self.active_action = QAction("Brak aktywnego projektu", self)
        self.active_action.setEnabled(False)
        tray_menu.addAction(self.active_action)
        
        tray_menu.addSeparator()
        
        settings_action = QAction("Ustawienia", self)
        settings_action.triggered.connect(self.open_settings)
        tray_menu.addAction(settings_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Zakończ", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_activated)
        self.tray_icon.show()
    
    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
    
    def show_window(self):
        self.show()
        self.raise_()
        self.activateWindow()
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Rubber Duck Assistant",
            "Aplikacja działa w tle. Użyj skrótu lub kliknij kaczkę.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def refresh_projects_list(self):
        self.projects_list.clear()
        for project in self.config_manager.projects.get("projects", []):
            item = QListWidgetItem(project["name"])
            item.setData(Qt.ItemDataRole.UserRole, project)
            self.projects_list.addItem(item)
        
        self.update_active_project_display()
    
    def update_active_project_display(self):
        active = self.config_manager.get_active_project()
        if active:
            self.active_project_label.setText(f"📂 {active['name']}")
            self.active_project_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
            
            desc_parts = []
            if active.get("tech_stack"):
                desc_parts.append(f"Stack: {', '.join(active['tech_stack'][:3])}")
            if active.get("description"):
                desc = active["description"][:100]
                if len(active["description"]) > 100:
                    desc += "..."
                desc_parts.append(desc)
            
            self.active_project_desc.setText(" | ".join(desc_parts))
            self.active_action.setText(f"Projekt: {active['name']}")
        else:
            self.active_project_label.setText("Brak aktywnego projektu")
            self.active_project_label.setStyleSheet("color: #666;")
            self.active_project_desc.setText("Dodaj projekt i aktywuj go aby rozpocząć")
            self.active_action.setText("Brak aktywnego projektu")
    
    def add_project(self):
        dialog = ProjectDialog(self)
        dialog.project_saved.connect(self._on_project_saved)
        dialog.exec()
    
    def _on_project_saved(self, project: dict):
        existing = [p["name"] for p in self.config_manager.projects.get("projects", [])]
        if project["name"] in existing:
            self.config_manager.update_project(project["name"], project)
        else:
            self.config_manager.add_project(project)
        self.refresh_projects_list()
    
    def edit_project(self):
        current = self.projects_list.currentItem()
        if not current:
            QMessageBox.information(self, "Info", "Wybierz projekt do edycji")
            return
        
        project_data = current.data(Qt.ItemDataRole.UserRole)
        dialog = ProjectDialog(self, project_data)
        dialog.project_saved.connect(self._on_project_saved)
        dialog.exec()
    
    def delete_project(self):
        current = self.projects_list.currentItem()
        if not current:
            QMessageBox.information(self, "Info", "Wybierz projekt do usunięcia")
            return
        
        project_name = current.text()
        reply = QMessageBox.question(
            self, "Potwierdź",
            f"Czy na pewno chcesz usunąć projekt '{project_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.remove_project(project_name)
            self.refresh_projects_list()
    
    def activate_project(self, item: QListWidgetItem):
        project_name = item.text()
        self.config_manager.set_active_project(project_name)
        self.update_active_project_display()
        self.tray_icon.showMessage(
            "Projekt aktywowany",
            f"Aktywny projekt: {project_name}",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def activate_selected_project(self):
        current = self.projects_list.currentItem()
        if current:
            self.activate_project(current)
        else:
            QMessageBox.information(self, "Info", "Wybierz projekt do aktywacji")
    
    def open_settings(self):
        dialog = SettingsDialog(self, self.config_manager.config)
        dialog.settings_saved.connect(self._on_settings_saved)
        dialog.exec()
    
    def _on_settings_saved(self, settings: dict):
        self.config_manager.config.update(settings)
        self.config_manager.save_config()
        QMessageBox.information(
            self, "Zapisano",
            "Ustawienia zostały zapisane. Niektóre zmiany wymagają restartu."
        )
