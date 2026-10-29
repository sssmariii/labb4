import sys
import csv
import re
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush, QFont
from PyQt6 import uic

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        uic.loadUi("task1.ui", self)
        
        self.data = []
        
        self.load_data("rez.csv") 
        self.setup_table()
        self.populate_filters()
        
    
        self.comboSchool.currentIndexChanged.connect(self.apply_filters)
        self.comboClass.currentIndexChanged.connect(self.apply_filters)
        
        self.apply_filters()

    def load_data(self, filename):
        
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    
                    match = re.search(r'sh-kaluga16-(\d+)-(\d+)-', row['login'])
                    if match:
                        row['school'] = match.group(1)
                        row['class'] = match.group(2)
                    else:
                        row['school'] = "Нет"
                        row['class'] = "Нет"
                    
                    try:
                        row['Score'] = int(row['Score'])
                    except ValueError:
                        row['Score'] = 0
                    self.data.append(row)
        except FileNotFoundError:
            print(f"Ошибка: Файл {filename} не найден в папке!")

    def setup_table(self):
        
        headers = ["Место", "Логин", "ФИО", "Суммарный балл"]
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def populate_filters(self):
        
        schools = sorted(set(str(r['school']) for r in self.data if r['school'] != "Нет"), key=int)
        classes = sorted(set(str(r['class']) for r in self.data if r['class'] != "Нет"), key=int)
        
        self.comboSchool.addItem("Все школы")
        self.comboSchool.addItems(schools)
        
        self.comboClass.addItem("Все классы")
        self.comboClass.addItems(classes)

    def apply_filters(self):
        
        selected_school = self.comboSchool.currentText()
        selected_class = self.comboClass.currentText()

        filtered = []
        for row in self.data:
            match_school = (selected_school == "Все школы" or str(row['school']) == selected_school)
            match_class = (selected_class == "Все классы" or str(row['class']) == selected_class)
            if match_school and match_class:
                filtered.append(row)

        filtered.sort(key=lambda x: x['Score'], reverse=True)
        
        places = {}
        if filtered:
            current_place = 1
            for i, row in enumerate(filtered):
                if i > 0 and row['Score'] < filtered[i-1]['Score']:
                    current_place = i + 1
                places[row['login']] = current_place

        self.tableWidget.setRowCount(len(filtered))
        for row_idx, row_data in enumerate(filtered):
            place = places.get(row_data['login'], '')
            
            items = [
                str(place),
                row_data['login'],
                row_data['user_name'],
                str(row_data['Score'])
            ]
            
            for col_idx, text in enumerate(items):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                if place == 1:
                    item.setBackground(QBrush(QColor(255, 215, 0)))
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                elif place == 2:
                    item.setBackground(QBrush(QColor(192, 192, 192)))
                elif place == 3:
                    item.setBackground(QBrush(QColor(205, 127, 50)))
                
                self.tableWidget.setItem(row_idx, col_idx, item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())