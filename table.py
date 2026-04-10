import sys
import re
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTableView, QLineEdit, 
                             QLabel, QStackedWidget, QMessageBox)
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt6.QtCore import Qt

class PaginatedModel(QSqlTableModel):
    def __init__(self, parent=None, db=None):
        super().__init__(parent, db)
        self.limit_val = 200
        self.offset_val = 0

    def selectStatement(self):
        table = self.tableName()
        f = self.filter()
        where_clause = f"WHERE {f}" if f else ""
        query = f"SELECT * FROM {table} {where_clause} LIMIT {self.limit_val} OFFSET {self.offset_val}"
        return query

class StudentManagement(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SSIS Pro - Multi-Table Management")
        self.setMinimumSize(1100, 750)

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("student_system.db")
        if not self.db.open():
            QMessageBox.critical(self, "Error", "Could not open database")
            sys.exit(1)

        self.current_page = 0
        self.page_size = 200

        self.init_models()
        self.init_ui()
        self.update_page_display()

    def init_models(self):
        self.college_model = QSqlTableModel(self, self.db)
        self.college_model.setTable("college")
        self.college_model.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)

        self.program_model = QSqlTableModel(self, self.db)
        self.program_model.setTable("program")
        self.program_model.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)

        self.student_model = PaginatedModel(self, self.db)
        self.student_model.setTable("student")
        self.student_model.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        nav_layout = QHBoxLayout()
        self.btn_students = QPushButton(" Students")
        self.btn_programs = QPushButton(" Programs")
        self.btn_colleges = QPushButton(" Colleges")
        for btn, idx in [(self.btn_students, 0), (self.btn_programs, 1), (self.btn_colleges, 2)]:
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            btn.clicked.connect(lambda _, i=idx: self.switch_tab(i))
            nav_layout.addWidget(btn)
        self.btn_students.setChecked(True)
        main_layout.addLayout(nav_layout)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search current table...")
        self.search_bar.textChanged.connect(self.search_data)
        main_layout.addWidget(self.search_bar)

        self.stack = QStackedWidget()
        self.student_view = QTableView()
        self.program_view = QTableView()
        self.college_view = QTableView()
        for v, m in [(self.student_view, self.student_model), (self.program_view, self.program_model), (self.college_view, self.college_model)]:
            v.setModel(m)
            v.setSortingEnabled(True)
            v.horizontalHeader().setStretchLastSection(True)
            self.stack.addWidget(v)
        main_layout.addWidget(self.stack)

        pagination_layout = QHBoxLayout()
        self.btn_prev = QPushButton(" ◀ Previous ")
        self.btn_next = QPushButton(" Next ▶ ")
        self.page_label = QLabel("Page 1 / 1")
        self.total_count_label = QLabel("Total Students: 0")
        self.total_count_label.setStyleSheet("font-weight: bold; color: #555; margin-left: 20px;")
        
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.btn_prev)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.btn_next)
        pagination_layout.addWidget(self.total_count_label)
        pagination_layout.addStretch()
        main_layout.addLayout(pagination_layout)

        action_layout = QHBoxLayout()
        btn_add = QPushButton(" ✚ Add Row")
        btn_save = QPushButton(" 💾 Update/Save Changes")
        btn_del = QPushButton(" 🗑 Delete Selected")
        btn_refresh = QPushButton(" ⏳ Refresh")
        btn_save.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        
        btn_add.clicked.connect(lambda: self.get_current_model_view()[0].insertRow(0))
        btn_save.clicked.connect(self.save_changes)
        btn_del.clicked.connect(self.delete_row)
        btn_refresh.clicked.connect(self.update_page_display)
        
        for btn in [btn_add, btn_save, btn_del, btn_refresh]:
            btn.setFixedHeight(35)
            action_layout.addWidget(btn)
        main_layout.addLayout(action_layout)

    def get_current_model_view(self):
        idx = self.stack.currentIndex()
        if idx == 0: return self.student_model, self.student_view
        if idx == 1: return self.program_model, self.program_view
        return self.college_model, self.college_view

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        self.btn_students.setChecked(index == 0)
        self.btn_programs.setChecked(index == 1)
        self.btn_colleges.setChecked(index == 2)
        self.current_page = 0
        self.search_bar.clear()
        self.update_page_display()

    def update_page_display(self):
        c_q = self.db.exec("SELECT college_code FROM college")
        v_c = []
        while c_q.next(): v_c.append(f"'{c_q.value(0)}'")
        c_list = ",".join(v_c) if v_c else "''"
        
        p_q = self.db.exec(f"SELECT program_code FROM program WHERE college_code IN ({c_list})")
        v_p = []
        while p_q.next(): v_p.append(f"'{p_q.value(0)}'")
        p_list = ",".join(v_p) if v_p else "''"

        model, _ = self.get_current_model_view()
        search_text = self.search_bar.text().strip()

        if isinstance(model, PaginatedModel):
            current_filter = f"program_code IN ({p_list})"
            if search_text:
                current_filter += f" AND (id LIKE '%{search_text}%' OR firstname LIKE '%{search_text}%' OR lastname LIKE '%{search_text}%' OR program_code LIKE '%{search_text}%' OR year LIKE '%{search_text}%' OR gender LIKE '%{search_text}%')"
            
            model.setFilter(current_filter)

            count_q = QSqlQuery(self.db)
            count_q.prepare(f"SELECT COUNT(*) FROM student WHERE {current_filter}")
            count_q.exec()
            total = 0
            if count_q.next(): total = count_q.value(0)
            
            self.total_count_label.setText(f"Total Students: {total}")
            self.total_count_label.setVisible(True)
            
            max_p = math.ceil(total / self.page_size) if total > 0 else 1
            model.limit_val = self.page_size
            model.offset_val = self.current_page * self.page_size
            model.select()
            
            self.page_label.setText(f"Page {self.current_page + 1} / {max_p}")
            self.btn_prev.setEnabled(self.current_page > 0)
            self.btn_next.setEnabled((self.current_page + 1) < max_p)
        else:
            self.total_count_label.setVisible(False)
            self.page_label.setText("Showing All")
            
            if model.tableName() == "program":
                f = f"college_code IN ({c_list})"
                
                if search_text: 
                    f += f" AND (program_code LIKE '%{search_text}%' OR program_name LIKE '%{search_text}%' OR college_code LIKE '%{search_text}%')"
                
                model.setFilter(f)
                
            elif model.tableName() == "college":
                if search_text: 
                    model.setFilter(f"college_code LIKE '%{search_text}%' OR college_name LIKE '%{search_text}%'")
                else: 
                    model.setFilter("")
                
            model.select()

    def search_data(self, text):
        self.current_page = 0
        self.update_page_display()

    def delete_row(self):
        m, v = self.get_current_model_view()
        idx = v.selectionModel().currentIndex()
        if idx.isValid() and QMessageBox.question(self, "Delete", "Confirm deletion?") == QMessageBox.StandardButton.Yes:
            m.removeRow(idx.row())
            m.submitAll()
            self.update_page_display()

    def save_changes(self):
        m, _ = self.get_current_model_view()
        if m.tableName() == "student":
            seen_ids = set()
            p_q = self.db.exec("SELECT program_code FROM program")
            valid_progs = []
            while p_q.next(): valid_progs.append(str(p_q.value(0)).strip())

            for r in range(m.rowCount()):
                sid = str(m.index(r, 0).data() or "").strip()
                fn = str(m.index(r, 1).data() or "").strip()
                ln = str(m.index(r, 2).data() or "").strip()
                prg = str(m.index(r, 3).data() or "").strip()
                yr = str(m.index(r, 4).data() or "").strip()
                gen = str(m.index(r, 5).data() or "").strip().capitalize()

                if not re.match(r"^(201[8-9]|202[0-6])-([0-1][0-9]{3}|2[0-4][0-9]{2}|2500)$", sid):
                    QMessageBox.warning(self, "Error", f"Row {r+1}: Invalid ID format."); return
                if sid in seen_ids:
                    QMessageBox.warning(self, "Error", f"Row {r+1}: Duplicate ID."); return
                seen_ids.add(sid)
                if not re.match(r"^[a-zA-Z\u00C0-\u017F\s\-]+$", fn) or not re.match(r"^[a-zA-Z\u00C0-\u017F\s\-]+$", ln):
                    QMessageBox.warning(self, "Error", f"Row {r+1}: Invalid name characters (letters/dashes/ñ only)."); return
                if prg not in valid_progs:
                    QMessageBox.warning(self, "Error", f"Row {r+1}: Program '{prg}' does not exist."); return
                if yr not in ["1", "2", "3", "4"]:
                    QMessageBox.warning(self, "Error", f"Row {r+1}: Year must be 1-4."); return
                if gen not in ["Male", "Female", "Other"]:
                    QMessageBox.warning(self, "Error", f"Row {r+1}: Use Male, Female, or Other."); return

        if m.submitAll():
            self.update_page_display()
            QMessageBox.information(self, "Success", "Saved.")
        else:
            QMessageBox.warning(self, "Error", m.lastError().text())

    def next_page(self): self.current_page += 1; self.update_page_display()
    def prev_page(self): self.current_page -= 1; self.update_page_display()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentManagement()
    window.show()
    sys.exit(app.exec())