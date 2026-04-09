import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTableView, QVBoxLayout, 
                             QWidget, QLineEdit, QPushButton, QHBoxLayout, QMessageBox)
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
from PyQt6.QtCore import Qt

class StudentSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SSIS Pro - Modern Student Management")
        self.resize(1000, 700)

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("student_system.db")
        if not self.db.open():
            QMessageBox.critical(self, "Error", "Could not open database file!")
            sys.exit(1)

        self.model = QSqlTableModel(self)
        self.model.setTable("student")
        self.model.select()

        self.model.setHeaderData(0, Qt.Orientation.Horizontal, "Student ID")
        self.model.setHeaderData(1, Qt.Orientation.Horizontal, "First Name")
        self.model.setHeaderData(2, Qt.Orientation.Horizontal, "Last Name")
        self.model.setHeaderData(3, Qt.Orientation.Horizontal, "Course")
        self.model.setHeaderData(4, Qt.Orientation.Horizontal, "Year")
        self.model.setHeaderData(5, Qt.Orientation.Horizontal, "Gender")

        main_layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search by Last Name or ID...")
        self.search_bar.textChanged.connect(self.search_data)
        search_layout.addWidget(self.search_bar)
        main_layout.addLayout(search_layout)

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("➕ Add New Row")
        del_btn = QPushButton("🗑️ Delete Selected")
        save_btn = QPushButton("💾 Save Changes")
        
        add_btn.clicked.connect(self.add_student)
        del_btn.clicked.connect(self.delete_student)
        save_btn.clicked.connect(lambda: self.model.submitAll())
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(del_btn)
        main_layout.addLayout(btn_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def search_data(self, text):
        filter_str = f"lastname LIKE '%{text}%' OR id LIKE '%{text}%'"
        self.model.setFilter(filter_str)
        self.model.select()

    def add_student(self):
        self.model.insertRow(self.model.rowCount())

    def delete_student(self):
        selected = self.table.selectionModel().currentIndex()
        if selected.isValid():
            confirm = QMessageBox.question(self, "Confirm", "Delete this record?", 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.model.removeRow(selected.row())
                self.model.select()
        else:
            QMessageBox.warning(self, "Selection", "Please click a row first!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    
    window = StudentSystem()
    window.show()
    sys.exit(app.exec())