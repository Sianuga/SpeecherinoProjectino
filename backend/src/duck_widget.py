from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen
import math

class DuckWidget(QWidget):
    clicked = pyqtSignal()
    
    def __init__(self, size=120):
        super().__init__()
        self.duck_size = size
        self.is_listening = False
        self.is_speaking = False
        self.animation_frame = 0
        self.pulse_value = 0
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(size + 40, size + 60)
        
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate)
        self.animation_timer.start(50)
        
        self._position_bottom_left()
    
    def _position_bottom_left(self):
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = 20
        y = screen.height() - self.height() - 60
        self.move(x, y)
    
    def _animate(self):
        self.animation_frame = (self.animation_frame + 1) % 360
        if self.is_listening or self.is_speaking:
            self.pulse_value = (math.sin(self.animation_frame * 0.1) + 1) / 2
        else:
            self.pulse_value = max(0, self.pulse_value - 0.05)
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2 - 10
        
        if self.is_listening:
            glow_color = QColor(76, 175, 80, int(100 * self.pulse_value))
            for i in range(3):
                radius = self.duck_size // 2 + 10 + i * 8
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(glow_color)
                painter.drawEllipse(
                    center_x - radius, 
                    center_y - radius, 
                    radius * 2, 
                    radius * 2
                )
        elif self.is_speaking:
            glow_color = QColor(33, 150, 243, int(100 * self.pulse_value))
            for i in range(3):
                radius = self.duck_size // 2 + 10 + i * 8
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(glow_color)
                painter.drawEllipse(
                    center_x - radius, 
                    center_y - radius, 
                    radius * 2, 
                    radius * 2
                )
        
        # Ciało kaczki (żółte)
        body_color = QColor(255, 213, 79)
        painter.setBrush(body_color)
        painter.setPen(QPen(QColor(200, 160, 50), 2))
        painter.drawEllipse(
            center_x - self.duck_size // 2,
            center_y - self.duck_size // 2 + 15,
            self.duck_size,
            self.duck_size - 20
        )
        
        # Głowa
        head_size = self.duck_size // 2
        head_y = center_y - self.duck_size // 4
        painter.drawEllipse(
            center_x - head_size // 2,
            head_y - head_size // 2,
            head_size,
            head_size
        )
        
        # Dziób (pomarańczowy)
        painter.setBrush(QColor(255, 152, 0))
        painter.setPen(QPen(QColor(200, 100, 0), 1))
        beak_points = [
            (center_x + head_size // 4, head_y - 2),
            (center_x + head_size // 2 + 15, head_y + 5),
            (center_x + head_size // 4, head_y + 10)
        ]
        from PyQt6.QtGui import QPolygon
        from PyQt6.QtCore import QPoint
        polygon = QPolygon([QPoint(int(x), int(y)) for x, y in beak_points])
        painter.drawPolygon(polygon)
        
        # Oczy
        eye_size = 8
        eye_y = head_y - 5
        painter.setBrush(QColor(0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - 2, eye_y, eye_size, eye_size)
        
        # Błysk w oku
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(center_x, eye_y + 1, 3, 3)
        
        # Status tekst
        painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        status_text = ""
        text_color = QColor(100, 100, 100)
        
        if self.is_listening:
            status_text = "🎤 Słucham..."
            text_color = QColor(76, 175, 80)
        elif self.is_speaking:
            status_text = "💬 Mówię..."
            text_color = QColor(33, 150, 243)
        
        if status_text:
            painter.setPen(text_color)
            text_rect = painter.fontMetrics().boundingRect(status_text)
            painter.drawText(
                center_x - text_rect.width() // 2,
                self.height() - 10,
                status_text
            )
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
    
    def set_listening(self, listening: bool):
        self.is_listening = listening
        self.is_speaking = False
        self.update()
    
    def set_speaking(self, speaking: bool):
        self.is_speaking = speaking
        self.is_listening = False
        self.update()
    
    def set_idle(self):
        self.is_listening = False
        self.is_speaking = False
        self.update()
