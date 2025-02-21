from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QListWidget, QTableWidget, \
    QTableWidgetItem, QPushButton, QHBoxLayout
import sys


class RobotMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot Monitoring System")
        self.setGeometry(100, 100, 800, 600)

        self.initUI()

    def initUI(self):
        self.tabs = QTabWidget()

        self.monitoring_tab = self.create_monitoring_tab()
        self.exception_handling_tab = self.create_exception_handling_tab()
        self.workflow_tab = QWidget()

        self.tabs.addTab(self.monitoring_tab, "Monitoring")
        self.tabs.addTab(self.exception_handling_tab, "Exception Handling")
        self.tabs.addTab(self.workflow_tab, "Workflow")

        self.setCentralWidget(self.tabs)

    def create_monitoring_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.robot_list = QListWidget()
        layout.addWidget(self.robot_list)

        tab.setLayout(layout)
        return tab

    def create_exception_handling_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.exception_table = QTableWidget()
        self.exception_table.setColumnCount(5)
        self.exception_table.setHorizontalHeaderLabels(
            ["Robot ID", "Error Type", "Time of Exception", "Time Handled", "Comment"])

        layout.addWidget(self.exception_table)
        tab.setLayout(layout)
        return tab

    def add_exception(self, robot_id, error_type, exception_time, handled_time, comment):
        row_position = self.exception_table.rowCount()
        self.exception_table.insertRow(row_position)

        self.exception_table.setItem(row_position, 0, QTableWidgetItem(robot_id))
        self.exception_table.setItem(row_position, 1, QTableWidgetItem(error_type))
        self.exception_table.setItem(row_position, 2, QTableWidgetItem(exception_time))
        self.exception_table.setItem(row_position, 3, QTableWidgetItem(handled_time))
        self.exception_table.setItem(row_position, 4, QTableWidgetItem(comment))

        mark_complete_button = QPushButton("Mark Complete")
        mark_complete_button.clicked.connect(lambda: self.mark_as_complete(row_position))
        self.exception_table.setCellWidget(row_position, 5, mark_complete_button)

    def mark_as_complete(self, row):
        self.exception_table.removeRow(row)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotMonitorApp()
    window.show()
    sys.exit(app.exec_())
