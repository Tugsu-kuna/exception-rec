from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
from core.monitor_thread import RobotMonitorThread

class RobotMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot Monitoring System")
        self.setGeometry(100, 100, 900, 600)
        self.initUI()

        self.monitor_thread = RobotMonitorThread()
        self.monitor_thread.update_signal.connect(self.update_monitoring_tab)
        self.monitor_thread.error_signal.connect(self.add_exception)
        self.monitor_thread.start()

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

        self.robot_table = QTableWidget()
        self.robot_table.setColumnCount(3)
        self.robot_table.setHorizontalHeaderLabels(["Robot ID", "Robot Type", "State"])
        layout.addWidget(self.robot_table)
        tab.setLayout(layout)
        return tab

    def create_exception_handling_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.exception_table = QTableWidget()
        self.exception_table.setColumnCount(7)
        self.exception_table.setColumnCount(7)
        self.exception_table.setHorizontalHeaderLabels(
            ["Robot ID", "Robot Type", "Error JSON", "Time of Exception", "Time Handled", "Error Type", "Action"]
        )

        layout.addWidget(self.exception_table)
        tab.setLayout(layout)
        return tab

    def update_monitoring_tab(self, robot_data):
        self.robot_table.setRowCount(0)
        for row_index, (robot_id, robot_type, state) in enumerate(robot_data):
            self.robot_table.insertRow(row_index)
            self.robot_table.setItem(row_index, 0, QTableWidgetItem(robot_id))
            self.robot_table.setItem(row_index, 1, QTableWidgetItem(robot_type))
            self.robot_table.setItem(row_index, 2, QTableWidgetItem(state))

    def add_exception(self, robot_id, robot_type, error_json, exception_time, handled_time="N/A", category="Unknown"):
        if error_json == "Resolved":
            self.update_exception_handled(robot_id, handled_time)
        else:
            row_position = self.exception_table.rowCount()
            self.exception_table.insertRow(row_position)
            self.exception_table.setItem(row_position, 0, QTableWidgetItem(robot_id))
            self.exception_table.setItem(row_position, 1, QTableWidgetItem(robot_type))
            self.exception_table.setItem(row_position, 2, QTableWidgetItem(error_json))
            self.exception_table.setItem(row_position, 3, QTableWidgetItem(exception_time))
            self.exception_table.setItem(row_position, 4, QTableWidgetItem(handled_time))
            self.exception_table.setItem(row_position, 5, QTableWidgetItem(category))

            mark_complete_button = QPushButton("Mark Complete")
            mark_complete_button.clicked.connect(lambda _, btn=mark_complete_button: self.mark_as_done(btn))
            self.exception_table.setCellWidget(row_position, 6, mark_complete_button)

    def update_exception_handled(self, robot_id, handled_time):
        for row in range(self.exception_table.rowCount()):
            if self.exception_table.item(row, 0).text() == robot_id:
                self.exception_table.setItem(row, 4, QTableWidgetItem(handled_time))
                return

    def mark_as_done(self, button):
        index = self.exception_table.indexAt(button.pos())
        row = index.row()
        if row >= 0:
            robot_id_item = self.exception_table.item(row, 0)
            if robot_id_item:
                robot_id = robot_id_item.text()
                self.monitor_thread.mark_robot_handled(robot_id)
            self.exception_table.removeRow(row)


    def closeEvent(self, event):
        self.monitor_thread.stop()
        event.accept()