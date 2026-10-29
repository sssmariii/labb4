import sys
import os
import sqlite3
import hashlib
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDialog, QMessageBox, 
                             QTableWidgetItem, QHeaderView, QFileDialog)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6 import uic

def init_db():
    conn = sqlite3.connect("library.db")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE,
        password TEXT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        year INTEGER,
        genre TEXT,
        image_path TEXT
    )""")
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- ОКНО АВТОРИЗАЦИИ ---
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("logintask6.ui", self) # ВАШЕ НАЗВАНИЕ
        self.setWindowTitle("Авторизация")
        self.btnLogin.clicked.connect(self.login)
        self.btnRegister.clicked.connect(self.register)

    def login(self):
        login = self.lineLogin.text().strip()
        password = self.linePassword.text().strip()
        
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        conn = sqlite3.connect("library.db")
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE login=?", (login,))
        result = cur.fetchone()
        conn.close()

        if result and result[0] == hash_password(password):
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

    def register(self):
        login = self.lineLogin.text().strip()
        password = self.linePassword.text().strip()
        
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        conn = sqlite3.connect("library.db")
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (login, password) VALUES (?, ?)", (login, hash_password(password)))
            conn.commit()
            QMessageBox.information(self, "Успех", "Вы успешно зарегистрированы! Теперь войдите.")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Ошибка", "Такой логин уже существует!")
        finally:
            conn.close()

# --- ОКНО ДОБАВЛЕНИЯ/РЕДАКТИРОВАНИЯ КНИГИ ---
class BookDialog(QDialog):
    def __init__(self, book_data=None):
        super().__init__()
        uic.loadUi("book_dialogtask6.ui", self) # ВАШЕ НАЗВАНИЕ
        self.image_path = None
        self.btnSelectImage.clicked.connect(self.select_image)

        if book_data:
            self.setWindowTitle("Редактировать книгу")
            self.lineTitle.setText(book_data[1])
            self.lineAuthor.setText(book_data[2])
            self.spinYear.setValue(book_data[3])
            self.lineGenre.setText(book_data[4])
            self.image_path = book_data[5]
            if self.image_path and os.path.exists(self.image_path):
                self.show_image(self.image_path)

    def select_image(self):
        # Открывает окно выбора файла
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите обложку", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            self.image_path = file_name
            self.show_image(file_name)

    def show_image(self, path):
        pixmap = QPixmap(path)
        self.labelImage.setPixmap(pixmap.scaled(150, 200, Qt.AspectRatioMode.KeepAspectRatio))

    def get_data(self):
        return {
            'title': self.lineTitle.text().strip(),
            'author': self.lineAuthor.text().strip(),
            'year': self.spinYear.value(),
            'genre': self.lineGenre.text().strip(),
            'image_path': self.image_path
        }

    def accept(self):
        if not self.lineTitle.text().strip() or not self.lineAuthor.text().strip():
            QMessageBox.warning(self, "Ошибка", "Название и автор обязательны!")
            return
        super().accept()

# --- ГЛАВНОЕ ОКНО ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("task6.ui", self)
        
        if not os.path.exists("images"):
            os.makedirs("images")

        self.btnAdd.clicked.connect(self.add_book)
        self.btnEdit.clicked.connect(self.edit_book)
        self.btnDelete.clicked.connect(self.delete_book)
        self.searchAuthor.textChanged.connect(self.load_data)
        self.searchTitle.textChanged.connect(self.load_data)
        self.tableWidget.itemSelectionChanged.connect(self.show_selected_image)
        
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Название", "Автор", "Год", "Жанр"])
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.setColumnHidden(0, True)
        
        self.current_books = []
        self.load_data()

    def load_data(self):
        author_filter = self.searchAuthor.text().strip()
        title_filter = self.searchTitle.text().strip()

        query = "SELECT * FROM books WHERE 1=1"
        params = []
        if author_filter:
            query += " AND author LIKE ?"
            params.append(f"%{author_filter}%")
        if title_filter:
            query += " AND title LIKE ?"
            params.append(f"%{title_filter}%")

        conn = sqlite3.connect("library.db")
        cur = conn.cursor()
        cur.execute(query, params)
        self.current_books = cur.fetchall()
        conn.close()

        self.tableWidget.setRowCount(len(self.current_books))
        for row_idx, book in enumerate(self.current_books):
            for col_idx in range(1, 5):
                self.tableWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(book[col_idx])))

    def show_selected_image(self):
        row = self.tableWidget.currentRow()
        if row < 0: return
        
        img_path = self.current_books[row][5]
        if img_path and os.path.exists(img_path):
            pixmap = QPixmap(img_path)
            self.labelBookImage.setPixmap(pixmap.scaled(200, 300, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.labelBookImage.setText("Нет фото")
            self.labelBookImage.setPixmap(QPixmap())

    def add_book(self):
        dialog = BookDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            
            final_img_path = None
            if data['image_path']:
                filename = os.path.basename(data['image_path'])
                final_img_path = os.path.join("images", filename)
                if data['image_path'] != final_img_path:
                    shutil.copy(data['image_path'], final_img_path)

            conn = sqlite3.connect("library.db")
            conn.execute("INSERT INTO books (title, author, year, genre, image_path) VALUES (?, ?, ?, ?, ?)",
                         (data['title'], data['author'], data['year'], data['genre'], final_img_path))
            conn.commit()
            conn.close()
            self.load_data()

    def edit_book(self):
        row = self.tableWidget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите книгу!")
            return
            
        book = self.current_books[row]
        dialog = BookDialog(book)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            
            final_img_path = data['image_path']
            if data['image_path'] and not data['image_path'].startswith("images"):
                filename = os.path.basename(data['image_path'])
                final_img_path = os.path.join("images", filename)
                shutil.copy(data['image_path'], final_img_path)

            conn = sqlite3.connect("library.db")
            conn.execute("UPDATE books SET title=?, author=?, year=?, genre=?, image_path=? WHERE id=?",
                         (data['title'], data['author'], data['year'], data['genre'], final_img_path, book[0]))
            conn.commit()
            conn.close()
            self.load_data()

    def delete_book(self):
        row = self.tableWidget.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите книгу!")
            return
            
        book = self.current_books[row]
        reply = QMessageBox.question(self, "Удаление", f"Удалить книгу '{book[1]}'?", 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = sqlite3.connect("library.db")
            conn.execute("DELETE FROM books WHERE id=?", (book[0],))
            conn.commit()
            conn.close()
            self.load_data()

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    
    login_win = LoginWindow()
    if login_win.exec() == QDialog.DialogCode.Accepted:
        main_win = MainWindow()
        main_win.show()
        sys.exit(app.exec())