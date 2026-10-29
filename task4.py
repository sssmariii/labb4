import sys
import random
import math
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QCursor
from PyQt6 import uic

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("task4.ui", self)
        
        
        self.setMouseTracking(True)
        self.centralwidget.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        
        global_pos = QCursor.pos()
        
        
        local_pos = self.centralwidget.mapFromGlobal(global_pos)
        
        
        btn_rect = self.btnRun.geometry()
        btn_center = btn_rect.center()
        
        
        distance = math.hypot(local_pos.x() - btn_center.x(), local_pos.y() - btn_center.y())
        
        
        if distance < 80:
            
            max_x = self.centralwidget.width() - self.btnRun.width()
            max_y = self.centralwidget.height() - self.btnRun.height()
            
        
            new_x = random.randint(0, max_x)
            new_y = random.randint(0, max_y)
            
            
            self.btnRun.move(new_x, new_y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())