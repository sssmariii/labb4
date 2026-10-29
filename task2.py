import sys
import sqlite3
import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem, 
                             QHeaderView, QDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6 import uic

class FilmDialog(QDialog):
    def __init__(self, db_connection, film_data=None):
        super().__init__()
        uic.loadUi("dialogtask2.ui", self)
        self.db = db_connection
        
        self.load_genres()
        
        if film_data:
            self.setWindowTitle("Редактировать фильм")
            self.lineEditTitle.setText(film_data['title'])
            self.spinBoxYear.setValue(film_data['year'])
            self.spinBoxDuration.setValue(film_data['duration'])
            
            index = self.comboBoxGenre.findData(film_data['genre'])
            if index >= 0:
                self.comboBoxGenre.setCurrentIndex(index)

    def load_genres(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT id, title FROM genres")
        for row in cursor.fetchall():
            self.comboBoxGenre.addItem(row[1], row[0])

    def accept(self):
        title = self.lineEditTitle.text().strip()
        year = self.spinBoxYear.value()
        duration = self.spinBoxDuration.value()
        current_year = datetime.datetime.now().year

        if not title:
            QMessageBox.warning(self, "Ошибка", "Название фильма не может быть пустым!")
            return
        
        if year > current_year or year < 1888:
            QMessageBox.warning(self, "Ошибка", f"Год должен быть от 1888 до {current_year}!")
            return
            
        if duration <= 0:
            QMessageBox.warning(self, "Ошибка", "Длительность должна быть больше нуля!")
            return

        super().accept()

    def get_data(self):
        return {
            'title': self.lineEditTitle.text().strip(),
            'year': self.spinBoxYear.value(),
            'genre': self.comboBoxGenre.currentData(),
            'duration': self.spinBoxDuration.value()
        }

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("task2.ui", self)
        
        try:
            self.db = sqlite3.connect("films_db.sqlite")
            self.db.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка БД", f"Не удалось подключиться: {e}")
            sys.exit(1)

        self.current_films_data = []

        self.btnAdd.clicked.connect(self.add_film)
        self.btnEdit.clicked.connect(self.edit_film)
        self.btnDelete.clicked.connect(self.delete_film)

        self.load_table()

    def load_table(self):
        cursor = self.db.cursor()
        query = """
            SELECT films.id, films.title, films.year, genres.title AS genre, films.duration 
            FROM films 
            LEFT JOIN genres ON films.genre = genres.id
        """
        cursor.execute(query)
        headers = [column[0] for column in cursor.description]
        
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers) 
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        rows = cursor.fetchall()
        self.tableWidget.setRowCount(len(rows))
        self.current_films_data = []

        for row_idx, row in enumerate(rows):
            self.current_films_data.append(row)
            items = [
                str(row['id']),
                row['title'],
                str(row['year']),
                row['genre'] if row['genre'] else "Неизвестно",
                str(row['duration'])
            ]
            
            for col_idx, text in enumerate(items):
                item = QTableWidgetItem(text)
                if col_idx != 1:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tableWidget.setItem(row_idx, col_idx, item)

    def add_film(self):
        dialog = FilmDialog(self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            cursor = self.db.cursor()
            cursor.execute(
                "INSERT INTO films (title, year, genre, duration) VALUES (?, ?, ?, ?)",
                (data['title'], data['year'], data['genre'], data['duration'])
            )
            self.db.commit()
            self.load_table()

    def edit_film(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Внимание", "Выберите фильм для редактирования!")
            return

        film_data = self.current_films_data[selected_row]
        dialog = FilmDialog(self.db, film_data)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            cursor = self.db.cursor()
            cursor.execute(
                "UPDATE films SET title=?, year=?, genre=?, duration=? WHERE id=?",
                (new_data['title'], new_data['year'], new_data['genre'], new_data['duration'], film_data['id'])
            )
            self.db.commit()
            self.load_table()

    def delete_film(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Внимание", "Выберите фильм для удаления!")
            return

        film_data = self.current_films_data[selected_row]
        
        reply = QMessageBox.question(
            self, "Подтверждение", 
            f"Вы уверены, что хотите удалить фильм '{film_data['title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM films WHERE id=?", (film_data['id'],))
            self.db.commit()
            self.load_table()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())