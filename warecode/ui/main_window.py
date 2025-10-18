from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QMessageBox
from core.monitor_thread import RobotMonitorThread
from ui.blacklist_tab import BlacklistTab
from core.session import save_session, load_session, clear_session
import time

class RobotMonitorApp(QMainWindow):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.setWindowTitle("Robot Monitoring System")
        self.setGeometry(100, 100, 900, 600)

        # Build UI first (creates self.completed_table)
        self.initUI()

        # Now it's safe to populate Completed tab
        self.populate_completed_from_json(session.get("completed_exceptions", []))

        # Start monitoring thread
        self.monitor_thread = RobotMonitorThread()
        self.monitor_thread.update_signal.connect(self.update_monitoring_tab)
        self.monitor_thread.error_signal.connect(self.add_exception)
        self.monitor_thread.start()

    def initUI(self):
        self.tabs = QTabWidget()
        self.monitoring_tab = self.create_monitoring_tab()
        self.exception_handling_tab = self.create_exception_handling_tab()
        self.completed_tab = self.create_completed_tab()
        self.workflow_tab = self.create_workflow_tab()
        self.blacklist_tab = BlacklistTab()
        self.tabs.addTab(self.monitoring_tab, "Monitoring")
        self.tabs.addTab(self.exception_handling_tab, "Exception Handling")
        self.tabs.addTab(self.completed_tab, "Completed Exceptions")
        self.tabs.addTab(self.blacklist_tab, "Blacklist")
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
            robot_id = self.exception_table.item(row, 0).text()
            robot_type = self.exception_table.item(row, 1).text()
            error_json = self.exception_table.item(row, 2).text()
            exception_time = self.exception_table.item(row, 3).text()
            handled_time = time.strftime("%Y-%m-%d %H:%M:%S")
            category = self.exception_table.item(row, 5).text()

            # Tell the thread this robot is handled
            self.monitor_thread.mark_robot_handled(robot_id)

            # Move to Completed tab
            completed_row = self.completed_table.rowCount()
            self.completed_table.insertRow(completed_row)
            self.completed_table.setItem(completed_row, 0, QTableWidgetItem(robot_id))
            self.completed_table.setItem(completed_row, 1, QTableWidgetItem(robot_type))
            self.completed_table.setItem(completed_row, 2, QTableWidgetItem(error_json))
            self.completed_table.setItem(completed_row, 3, QTableWidgetItem(exception_time))
            self.completed_table.setItem(completed_row, 4, QTableWidgetItem(handled_time))
            self.completed_table.setItem(completed_row, 5, QTableWidgetItem(category))

            # Remove from active table
            self.exception_table.removeRow(row)

            # Append to JSON
            record = {
                "robot_id": robot_id,
                "robot_type": robot_type,
                "error": error_json,
                "time_of_exception": exception_time,
                "time_handled": handled_time,
                "category": category,
                "employee": self.session["employee"]
            }
            self.session["completed_exceptions"].append(record)
            save_session(self.session)

    def create_workflow_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        logout_btn = QPushButton("End Session (Logout)")
        logout_btn.clicked.connect(self.end_session)

        layout.addWidget(logout_btn)
        tab.setLayout(layout)
        return tab

    def end_session(self):
        confirm = QMessageBox.question(
            self, "End Session", "End session and clear data?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            clear_session()
            QMessageBox.information(self, "Session Ended", "Session cleared for next shift.")
            self.close()

    def create_completed_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.completed_table = QTableWidget()
        self.completed_table.setColumnCount(6)
        self.completed_table.setHorizontalHeaderLabels(
            ["Robot ID", "Robot Type", "Error JSON", "Time of Exception", "Time Handled", "Error Type"]
        )

        layout.addWidget(self.completed_table)
        tab.setLayout(layout)
        return tab

    def populate_completed_from_json(self, data):
        self.completed_table.setRowCount(0)
        for record in data:
            row = self.completed_table.rowCount()
            self.completed_table.insertRow(row)
            self.completed_table.setItem(row, 0, QTableWidgetItem(record["robot_id"]))
            self.completed_table.setItem(row, 1, QTableWidgetItem(record["robot_type"]))
            self.completed_table.setItem(row, 2, QTableWidgetItem(record["error"]))
            self.completed_table.setItem(row, 3, QTableWidgetItem(record["time_of_exception"]))
            self.completed_table.setItem(row, 4, QTableWidgetItem(record["time_handled"]))
            self.completed_table.setItem(row, 5, QTableWidgetItem(record["category"]))
    def closeEvent(self, event):
        self.monitor_thread.stop()
        event.accept()