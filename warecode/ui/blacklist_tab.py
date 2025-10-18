from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QFileDialog, QMessageBox
from core.blacklist import load_blacklist, save_blacklist

class BlacklistTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ranges = load_blacklist()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Table to show blacklist ranges
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Start", "End (None=open)"])
        layout.addWidget(self.table)

        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Range")
        remove_btn = QPushButton("Remove Selected")
        save_btn = QPushButton("Save Blacklist")

        add_btn.clicked.connect(self.add_range)
        remove_btn.clicked.connect(self.remove_selected)
        save_btn.clicked.connect(self.save_ranges)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.load_ranges_into_table()

    def load_ranges_into_table(self):
        self.table.setRowCount(0)
        for start, end in self.ranges:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(start)))
            self.table.setItem(row, 1, QTableWidgetItem("" if end is None else str(end)))

    def add_range(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem("0"))
        self.table.setItem(row, 1, QTableWidgetItem(""))

    def remove_selected(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.table.removeRow(selected)

    def save_ranges(self):
        new_ranges = []
        for row in range(self.table.rowCount()):
            start_item = self.table.item(row, 0)
            end_item = self.table.item(row, 1)
            try:
                start = int(start_item.text()) if start_item else 0
                end_text = end_item.text().strip() if end_item else ""
                end = int(end_text) if end_text else None
                new_ranges.append((start, end))
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", f"Row {row+1} has invalid numbers.")
                return

        self.ranges = new_ranges
        save_blacklist(self.ranges)
        QMessageBox.information(self, "Saved", "Blacklist updated successfully.")
