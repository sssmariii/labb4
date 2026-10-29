import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtGui import QPainter, QColor, QPolygon, QCursor
from PyQt6.QtCore import Qt, QPoint
from PyQt6 import uic

class DrawingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.shapes = []
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet("background-color: white;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        for shape in self.shapes:
            painter.setBrush(shape['color'])
            painter.setPen(Qt.PenStyle.NoPen)
            
            if shape['type'] == 'circle':
                r = shape['size'] // 2
                painter.drawEllipse(shape['x'] - r, shape['y'] - r, r * 2, r * 2)
            
            elif shape['type'] == 'square':
                half = shape['size'] // 2
                painter.drawRect(shape['x'] - half, shape['y'] - half, shape['size'], shape['size'])
            
            elif shape['type'] == 'triangle':
                half = shape['size'] // 2
                points = [
                    QPoint(shape['x'], shape['y'] - half),
                    QPoint(shape['x'] - half, shape['y'] + half),
                    QPoint(shape['x'] + half, shape['y'] + half)
                ]
                polygon = QPolygon(points)
                painter.drawPolygon(polygon)

    def mousePressEvent(self, event):
        x = int(event.position().x())
        y = int(event.position().y())
        size = random.randint(30, 80)
        color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        if event.button() == Qt.MouseButton.LeftButton:
            self.shapes.append({'type': 'circle', 'x': x, 'y': y, 'size': size, 'color': color})
        elif event.button() == Qt.MouseButton.RightButton:
            self.shapes.append({'type': 'square', 'x': x, 'y': y, 'size': size, 'color': color})
            
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            global_pos = QCursor.pos()
            local_pos = self.mapFromGlobal(global_pos)
            x = local_pos.x()
            y = local_pos.y()
            size = random.randint(30, 80)
            color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            
            self.shapes.append({'type': 'triangle', 'x': x, 'y': y, 'size': size, 'color': color})
            self.update()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("task3.ui", self)
        
        self.drawing_widget = DrawingWidget()
        self.setCentralWidget(self.drawing_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())