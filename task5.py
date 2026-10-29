import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush
from PyQt6.QtCore import Qt
from PyQt6 import uic

def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path("task5.ui"), self)
        
        self.ufo_size = 60
        self.step = 20
        
        pixmap = QPixmap(resource_path("ufo.png"))
        if not pixmap.isNull():
            pixmap = pixmap.scaled(self.ufo_size, self.ufo_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.ufoLabel.setPixmap(pixmap)
        else:
            self.ufoLabel.setText("UFO")
            self.ufoLabel.setStyleSheet("background-color: lightblue; border-radius: 30px; font-weight: bold;")
        
        self.ufoLabel.resize(self.ufo_size, self.ufo_size)

        self.ufoLabel.move(100, 100)

    def keyPressEvent(self, event):
        x = self.ufoLabel.x()
        y = self.ufoLabel.y()
        
        form_w = self.centralwidget.width()
        form_h = self.centralwidget.height()
        ufo_w = self.ufoLabel.width()
        ufo_h = self.ufoLabel.height()

        if event.key() == Qt.Key.Key_Left:
            x -= self.step
            if x + ufo_w < 0:  
                x = form_w
        elif event.key() == Qt.Key.Key_Right:
            x += self.step
            if x > form_w:     
                x = -ufo_w
        elif event.key() == Qt.Key.Key_Up:
            y -= self.step
            if y + ufo_h < 0:  
                y = form_h
        elif event.key() == Qt.Key.Key_Down:
            y += self.step
            if y > form_h:     
                y = -ufo_h

        self.ufoLabel.move(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())