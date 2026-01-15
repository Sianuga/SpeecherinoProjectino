from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QListWidget, QListWidgetItem,
    QTabWidget, QWidget, QFormLayout, QComboBox, QSpinBox,
    QMessageBox, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class ProjectDialog(QDialog):
    project_saved = pyqtSignal(dict)

    def __init__(self, parent=None, project_data=None):
        super().__init__(parent)
        self.project_data = project_data or {}
        self.setWindowTitle("Konfiguracja Projektu" if not project_data else "Edytuj Projekt")
        self.setMinimumSize(500, 500)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Nazwa projektu
        name_layout = QHBoxLayout()
        name_label = QLabel("Nazwa projektu:")
        name_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        name_layout.addWidget(name_label)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("np. E-commerce Backend")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Opis projektu
        desc_label = QLabel("Opis projektu:")
        desc_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        layout.addWidget(desc_label)
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText(
            "Opisz nad czym pracujesz, jaki jest cel projektu, "
            "jakie problemy rozwiązuje..."
        )
        self.description_edit.setMaximumHeight(120)
        layout.addWidget(self.description_edit)

        # Stack technologiczny
        tech_group = QGroupBox("Stack Technologiczny")
        tech_layout = QVBoxLayout()

        tech_input_layout = QHBoxLayout()
        self.tech_input = QLineEdit()
        self.tech_input.setPlaceholderText("np. Python, FastAPI, PostgreSQL")
        self.tech_input.returnPressed.connect(self.add_tech)
        tech_input_layout.addWidget(self.tech_input)

        add_tech_btn = QPushButton("Dodaj")
        add_tech_btn.clicked.connect(self.add_tech)
        tech_input_layout.addWidget(add_tech_btn)
        tech_layout.addLayout(tech_input_layout)

        self.tech_list = QListWidget()
        self.tech_list.setMaximumHeight(100)
        tech_layout.addWidget(self.tech_list)

        remove_tech_btn = QPushButton("Usuń zaznaczone")
        remove_tech_btn.clicked.connect(self.remove_tech)
        tech_layout.addWidget(remove_tech_btn)

        tech_group.setLayout(tech_layout)
        layout.addWidget(tech_group)

        # Założenia biznesowe
        business_label = QLabel("Główne założenia biznesowe:")
        business_label.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        layout.addWidget(business_label)
        self.business_edit = QTextEdit()
        self.business_edit.setPlaceholderText(
            "Opisz kluczowe wymagania biznesowe, ograniczenia, "
            "cele które projekt ma osiągnąć..."
        )
        self.business_edit.setMaximumHeight(100)
        layout.addWidget(self.business_edit)

        # Dodatkowy kontekst
        context_label = QLabel("Dodatkowy kontekst (opcjonalnie):")
        context_label.setStyleSheet("color: #b0b0b0;")
        layout.addWidget(context_label)
        self.context_edit = QTextEdit()
        self.context_edit.setPlaceholderText(
            "Dodatkowe informacje które mogą pomóc kaczce zrozumieć projekt..."
        )
        self.context_edit.setMaximumHeight(80)
        layout.addWidget(self.context_edit)

        # Przyciski
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Anuluj")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Zapisz")
        save_btn.setDefault(True)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a6a4a;
                border-color: #5a7a5a;
            }
            QPushButton:hover {
                background-color: #5a7a5a;
                border-color: #ffd54f;
            }
        """)
        save_btn.clicked.connect(self.save_project)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

    def load_data(self):
        if self.project_data:
            self.name_edit.setText(self.project_data.get("name", ""))
            self.description_edit.setPlainText(self.project_data.get("description", ""))
            self.business_edit.setPlainText(self.project_data.get("business_assumptions", ""))
            self.context_edit.setPlainText(self.project_data.get("additional_context", ""))
            for tech in self.project_data.get("tech_stack", []):
                self.tech_list.addItem(tech)

    def add_tech(self):
        tech = self.tech_input.text().strip()
        if tech:
            self.tech_list.addItem(tech)
            self.tech_input.clear()

    def remove_tech(self):
        for item in self.tech_list.selectedItems():
            self.tech_list.takeItem(self.tech_list.row(item))

    def save_project(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Błąd", "Nazwa projektu jest wymagana!")
            return

        tech_stack = [
            self.tech_list.item(i).text()
            for i in range(self.tech_list.count())
        ]

        project = {
            "name": name,
            "description": self.description_edit.toPlainText().strip(),
            "tech_stack": tech_stack,
            "business_assumptions": self.business_edit.toPlainText().strip(),
            "additional_context": self.context_edit.toPlainText().strip()
        }

        self.project_saved.emit(project)
        self.accept()


class SettingsDialog(QDialog):
    settings_saved = pyqtSignal(dict)

    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.config = config or {}
        self.setWindowTitle("Ustawienia")
        self.setMinimumSize(450, 400)
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        tabs = QTabWidget()

        # Tab: Ogólne
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        general_layout.setSpacing(15)

        hotkey_label = QLabel("Skrót Push-to-Talk:")
        hotkey_label.setStyleSheet("color: #e0e0e0;")
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setPlaceholderText("ctrl+shift+d")
        general_layout.addRow(hotkey_label, self.hotkey_edit)

        size_label = QLabel("Rozmiar kaczki:")
        size_label.setStyleSheet("color: #e0e0e0;")
        self.duck_size_spin = QSpinBox()
        self.duck_size_spin.setRange(80, 200)
        self.duck_size_spin.setValue(120)
        general_layout.addRow(size_label, self.duck_size_spin)

        self.tts_checkbox = QCheckBox("Włącz odpowiedzi głosowe (TTS)")
        self.tts_checkbox.setChecked(True)
        self.tts_checkbox.setStyleSheet("color: #e0e0e0;")
        general_layout.addRow(self.tts_checkbox)

        tabs.addTab(general_tab, "Ogólne")

        # Tab: API
        api_tab = QWidget()
        api_layout = QFormLayout(api_tab)
        api_layout.setSpacing(15)

        # ElevenLabs - główny provider STT/TTS
        elevenlabs_label = QLabel("ElevenLabs API Key (STT/TTS):")
        elevenlabs_label.setStyleSheet("color: #e0e0e0;")
        self.elevenlabs_key = QLineEdit()
        self.elevenlabs_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.elevenlabs_key.setPlaceholderText("Klucz z elevenlabs.io")
        api_layout.addRow(elevenlabs_label, self.elevenlabs_key)

        # Anthropic - LLM
        anthropic_label = QLabel("Anthropic API Key (LLM):")
        anthropic_label.setStyleSheet("color: #e0e0e0;")
        self.anthropic_key = QLineEdit()
        self.anthropic_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.anthropic_key.setPlaceholderText("sk-ant-...")
        api_layout.addRow(anthropic_label, self.anthropic_key)

        # Google - opcjonalny
        google_label = QLabel("Google API Key (opcjonalny):")
        google_label.setStyleSheet("color: #e0e0e0;")
        self.google_key = QLineEdit()
        self.google_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.google_key.setPlaceholderText("AIza...")
        api_layout.addRow(google_label, self.google_key)

        provider_label = QLabel("Dostawca LLM:")
        provider_label.setStyleSheet("color: #e0e0e0;")
        self.llm_provider = QComboBox()
        self.llm_provider.addItems(["claude", "gemini"])
        api_layout.addRow(provider_label, self.llm_provider)

        tabs.addTab(api_tab, "API Keys")

        layout.addWidget(tabs)

        # Przyciski
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Anuluj")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Zapisz")
        save_btn.setDefault(True)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a6a4a;
                border-color: #5a7a5a;
            }
            QPushButton:hover {
                background-color: #5a7a5a;
                border-color: #ffd54f;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_btn)

        layout.addLayout(buttons_layout)

    def load_config(self):
        self.hotkey_edit.setText(self.config.get("push_to_talk_key", "ctrl+shift+d"))
        self.duck_size_spin.setValue(self.config.get("duck_size", 120))
        self.tts_checkbox.setChecked(self.config.get("tts_enabled", True))

        api_keys = self.config.get("api_keys", {})
        self.elevenlabs_key.setText(api_keys.get("elevenlabs", ""))
        self.anthropic_key.setText(api_keys.get("anthropic", ""))
        self.google_key.setText(api_keys.get("google", ""))

        provider = self.config.get("llm_provider", "claude")
        index = self.llm_provider.findText(provider)
        if index >= 0:
            self.llm_provider.setCurrentIndex(index)

    def save_settings(self):
        settings = {
            "push_to_talk_key": self.hotkey_edit.text().strip() or "ctrl+shift+d",
            "duck_size": self.duck_size_spin.value(),
            "tts_enabled": self.tts_checkbox.isChecked(),
            "llm_provider": self.llm_provider.currentText(),
            "api_keys": {
                "elevenlabs": self.elevenlabs_key.text().strip(),
                "anthropic": self.anthropic_key.text().strip(),
                "google": self.google_key.text().strip()
            }
        }
        self.settings_saved.emit(settings)
        self.accept()