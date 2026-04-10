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
        self.student_view.setSortingEnabled(True)
        self.stack.addWidget(self.student_view)

        self.program_model = QSqlTableModel(self)
        self.program_model.setTable("program")
        self.program_model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.program_model.select()
        self.program_view = QTableView()
        self.program_view.setModel(self.program_model)
        self.program_view.setSortingEnabled(True)
        self.stack.addWidget(self.program_view)

        self.college_model = QSqlTableModel(self)
        self.college_model.setTable("college")
        self.college_model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.college_model.select()
        self.college_view = QTableView()
        self.college_view.setModel(self.college_model)
        self.college_view.setSortingEnabled(True)
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

    def get_current_model_view(self):
        """Helper to find out which table is currently visible."""
        idx = self.stack.currentIndex()
        if idx == 0: return self.student_model, self.student_view
        if idx == 1: return self.program_model, self.program_view
        return self.college_model, self.college_view

    def search_data(self, text):
        model, _ = self.get_current_model_view()
        table_name = model.tableName()
        text = text.strip()

        # 1. First, get the "Soft Delete" base filter 
        # (This ensures we don't show students of deleted colleges during a search)
        if table_name == "student":
            # We need to re-run the logic to see which programs are currently valid
            college_query = self.db.exec("SELECT college_code FROM college")
            valid_cols = []
            while college_query.next(): valid_cols.append(f"'{college_query.value(0)}'")
            col_list = ",".join(valid_cols) if valid_cols else "''"
            
            prog_query = self.db.exec(f"SELECT program_code FROM program WHERE college_code IN ({col_list})")
            valid_progs = []
            while prog_query.next(): valid_progs.append(f"'{prog_query.value(0)}'")
            prog_list = ",".join(valid_progs) if valid_progs else "''"
            
            base_filter = f"program_code IN ({prog_list})"
        else:
            base_filter = "1=1" # Means "show everything" for other tables

        # 2. Build the Search Filter
        if not text:
            # If search is empty, just use the base visibility filter
            model.setFilter(base_filter)
        else:
            if table_name == "student":
                # Search across ALL student columns
                search_filter = (f"({base_filter}) AND ("
                                f"id LIKE '%{text}%' OR "
                                f"firstname LIKE '%{text}%' OR "
                                f"lastname LIKE '%{text}%' OR "
                                f"program_code LIKE '%{text}%' OR "
                                f"year LIKE '%{text}%' OR "
                                f"gender LIKE '%{text}%')")
            elif table_name == "program":
                search_filter = (f"program_code LIKE '%{text}%' OR "
                                f"program_name LIKE '%{text}%' OR "
                                f"college_code LIKE '%{text}%'")
            else: # college
                search_filter = (f"college_code LIKE '%{text}%' OR "
                                f"college_name LIKE '%{text}%'")
            
            model.setFilter(search_filter)

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
            confirm = QMessageBox.question(self, "Confirm Delete", 
                                         "This will hide related data across all tabs. Proceed?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                model.removeRow(index.row())
                if model.submitAll():
                    self.student_model.select()
                    self.program_model.select()
                    self.college_model.select()
                    self.apply_filters() 
                else:
                    QMessageBox.warning(self, "Error", "Could not delete row.")
        else:
            QMessageBox.warning(self, "Selection", "Select a row first.")
            
    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        self.btn_students.setChecked(index == 0)
        self.btn_programs.setChecked(index == 1)
        self.btn_colleges.setChecked(index == 2)
        self.apply_filters()
        
    def apply_filters(self):
        """Requirement: Hide students/programs if their parent is 'deleted'"""
        self.student_model.blockSignals(True)
        self.program_model.blockSignals(True)

        try:
            college_query = self.db.exec("SELECT college_code FROM college")
            valid_colleges = []
            while college_query.next():
                valid_colleges.append(f"'{college_query.value(0)}'")
            
            col_list = ",".join(valid_colleges) if valid_colleges else "'EMPTY_DB'"

            self.program_model.setFilter(f"college_code IN ({col_list})")
            self.program_model.select()

            program_query = self.db.exec(f"SELECT program_code FROM program WHERE college_code IN ({col_list})")
            valid_programs = []
            while program_query.next():
                valid_programs.append(f"'{program_query.value(0)}'")
            
            prog_list = ",".join(valid_programs) if valid_programs else "'EMPTY_DB'"

            self.student_model.setFilter(f"program_code IN ({prog_list})")
            self.student_model.select()

        except Exception as e:
            print(f"Filter Error: {e}")
        
        self.student_model.blockSignals(False)
        self.program_model.blockSignals(False)
        
        _, view = self.get_current_model_view()
        view.sortByColumn(view.horizontalHeader().sortIndicatorSection(), 
                          view.horizontalHeader().sortIndicatorOrder())
    def save_changes(self):
        model, _ = self.get_current_model_view()
        
        if model.submitAll():
            self.student_model.select()
            self.program_model.select()
            self.college_model.select()
            
            self.apply_filters()
            
            QMessageBox.information(self, "Success", "Changes saved and all views updated!")
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