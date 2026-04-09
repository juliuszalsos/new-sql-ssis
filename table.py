import sys
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableView, QVBoxLayout, 
                             QWidget, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QStackedWidget, QLabel)
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtCore import Qt

class StudentSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SSIS Pro - Multi-Table Management")
        self.resize(1100, 750)

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("student_system.db")
        if not self.db.open():
            QMessageBox.critical(self, "Error", "Could not open database!")
            sys.exit(1)

        self.student_model = QSqlTableModel(self)
        self.student_model.setTable("student")
        
        self.student_model.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        self.student_model.select()

        main_layout = QVBoxLayout()

        nav_layout = QHBoxLayout()
        self.btn_students = QPushButton("👥 Students")
        self.btn_programs = QPushButton("🎓 Programs")
        self.btn_colleges = QPushButton("🏛️ Colleges")
        
        for btn in [self.btn_students, self.btn_programs, self.btn_colleges]:
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            nav_layout.addWidget(btn)
            
        self.btn_students.setChecked(True)
        main_layout.addLayout(nav_layout)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search current table...")
        self.search_bar.textChanged.connect(self.search_data)
        main_layout.addWidget(self.search_bar)

        self.stack = QStackedWidget()

        self.student_model = QSqlTableModel(self)
        self.student_model.setTable("student")
        self.student_model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.student_model.select()
        self.student_view = QTableView()
        self.student_view.setModel(self.student_model)
        self.stack.addWidget(self.student_view)

        self.program_model = QSqlTableModel(self)
        self.program_model.setTable("program")
        self.program_model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.program_model.select()
        self.program_view = QTableView()
        self.program_view.setModel(self.program_model)
        self.stack.addWidget(self.program_view)

        self.college_model = QSqlTableModel(self)
        self.college_model.setTable("college")
        self.college_model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.college_model.select()
        self.college_view = QTableView()
        self.college_view.setModel(self.college_model)
        self.stack.addWidget(self.college_view)

        main_layout.addWidget(self.stack)

        self.btn_students.clicked.connect(lambda: self.switch_tab(0))
        self.btn_programs.clicked.connect(lambda: self.switch_tab(1))
        self.btn_colleges.clicked.connect(lambda: self.switch_tab(2))

        crud_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add Row")
        save_btn = QPushButton("🔄 Update/Save Changes") 
        del_btn = QPushButton("🗑️ Delete Selected")
        refresh_btn = QPushButton("⌛ Refresh")

        add_btn.clicked.connect(self.add_row)
        save_btn.clicked.connect(self.save_changes)
        del_btn.clicked.connect(self.delete_row)
        refresh_btn.clicked.connect(self.refresh_table)

        save_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        
        crud_layout.addWidget(add_btn)
        crud_layout.addWidget(save_btn)
        crud_layout.addWidget(del_btn)
        crud_layout.addWidget(refresh_btn)
        main_layout.addLayout(crud_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        self.btn_students.setChecked(index == 0)
        self.btn_programs.setChecked(index == 1)
        self.btn_colleges.setChecked(index == 2)
        self.search_data(self.search_bar.text())

    def get_current_model_view(self):
        """Helper to find out which table is currently visible."""
        idx = self.stack.currentIndex()
        if idx == 0: return self.student_model, self.student_view
        if idx == 1: return self.program_model, self.program_view
        return self.college_model, self.college_view

    def search_data(self, text):
        model, _ = self.get_current_model_view()
        table_name = model.tableName()

        if table_name == "student":
            filter_str = f"lastname LIKE '%{text}%' OR id LIKE '%{text}%'"
        elif table_name == "program":
            filter_str = f"name LIKE '%{text}%' OR code LIKE '%{text}%'"
        else:
            filter_str = f"name LIKE '%{text}%' OR code LIKE '%{text}%'"
            
        model.setFilter(filter_str)
        model.select()

    def add_row(self):
        model, view = self.get_current_model_view()
        row = model.rowCount()
        model.insertRow(row)
        view.scrollToBottom()

    def delete_row(self):
        model, view = self.get_current_model_view()
        index = view.selectionModel().currentIndex()
        if index.isValid():
            model.removeRow(index.row())
            model.select()
            
    def save_changes(self):
        model, _ = self.get_current_model_view()
        
        if model.tableName() == "student":
            for row in range(model.rowCount()):
                s_id = str(model.index(row, 0).data()).strip()
                fname = str(model.index(row, 1).data()).strip()
                lname = str(model.index(row, 2).data()).strip()
                year_lvl = str(model.index(row, 4).data()).strip()
                gender = str(model.index(row, 5).data()).strip().capitalize()

                id_pattern = r"^(201[8-9]|202[0-6])-([0-1][0-9]{3}|2[0-4][0-9]{2}|2500)$"                
                if not re.match(id_pattern, s_id) or s_id.endswith("-0000"):
                    QMessageBox.warning(self, "Invalid ID", f"Row {row+1}: ID '{s_id}' is invalid.\nYear: 2018-2026, Range: 0001-2500")
                    return

                if any(char.isdigit() for char in fname) or any(char.isdigit() for char in lname):
                    QMessageBox.warning(self, "Invalid Name", f"Row {row+1}: Names cannot contain numbers!")
                    return

                if year_lvl not in ["1", "2", "3", "4"]:
                    QMessageBox.warning(self, "Invalid Year", f"Row {row+1}: Year Level must be 1, 2, 3, or 4.")
                    return
                if gender not in ["Male", "Female", "Other"]:
                    QMessageBox.warning(self, "Invalid Gender", f"Row {row+1}: Gender must be 'Male', 'Female', or 'Other'.\n(You entered: '{gender}')")
                    return

        if model.submitAll():
            QMessageBox.information(self, "Success", "All records validated and saved!")
        else:
            QMessageBox.warning(self, "Error", f"Database error: {model.lastError().text()}")
    
    def refresh_table(self):
        """Reloads data from the database file"""
        model, _ = self.get_current_model_view()
        model.select()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = StudentSystem()
    window.show()
    sys.exit(app.exec())