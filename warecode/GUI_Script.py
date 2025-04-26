import sys
import requests
import time
import os
import json
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QTableWidget, \
    QTableWidgetItem, QPushButton, QHBoxLayout, QLineEdit

# ESS API URL and Headers for Robot Status
ess_ip = 'http://10.251.3.25:9000/'
query_type_url = ess_ip + 'ess-api/model/queryModelByType?modelType=robot'
headers = {'Content-Type': 'application/json', 'accept': 'application/json'}

# Log file path
log_file_path = "D:\\Project\\warecode\\exception.txt"


# The Robot Monitor Thread that checks the robot states every 1 second
class RobotMonitorThread(QThread):
    update_signal = pyqtSignal(list)  # Signal to update the monitoring tab
    error_signal = pyqtSignal(str, str, str, str, str)  # (Robot Name, Robot Type, Error JSON, Start Time, Handled Time)

    def __init__(self):
        super().__init__()
        self.running = True
        self.error_logs = {}

    def run(self):
        while self.running:
            try:
                response = requests.get(query_type_url, headers=headers)
                if response.status_code != 200:
                    print(f"⚠️ API Error {response.status_code}")
                    time.sleep(1)
                    continue

                result = response.json()
                if 'data' not in result or 'robot' not in result['data']:
                    print("⚠️ Invalid API Response")
                    time.sleep(1)
                    continue

                robots = result['data']['robot']
                robot_data = []
                for robot in robots:
                    name = robot.get('code', 'Unknown Robot')
                    state = robot.get('hardwareState', 'UNKNOWN')
                    robot_type = robot.get('robotTypeCode', 'UNKNOWN')
                    error_info = robot.get('otherHardwareInfo', {}).get('errorState', [])

                    # Classify robot type
                    if robot_type == "RT_KUBOT":
                        display_type = "Big Robot"
                    elif robot_type == "RT_KUBOT_MINI_HAIFLEX":
                        display_type = "Small Robot"
                    else:
                        display_type = "Unknown Type"

                    robot_data.append((name, display_type, state))

                    if state == "ROBOT_ABNORMAL" and error_info:
                        error_json = json.dumps(error_info, indent=2)
                        if name not in self.error_logs:
                            start_time = time.strftime("%Y-%m-%d %H:%M:%S")
                            self.error_logs[name] = start_time
                            self.error_signal.emit(name, display_type, error_json, start_time, "N/A")
                    elif name in self.error_logs:
                        handled_time = time.strftime("%Y-%m-%d %H:%M:%S")
                        self.error_signal.emit(name, display_type, "Resolved", self.error_logs[name], handled_time)
                        del self.error_logs[name]

                self.update_signal.emit(robot_data)
            except Exception as e:
                print(f"🚨 Error: {str(e)}")
            time.sleep(1)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


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
        self.exception_table.setHorizontalHeaderLabels(
            ["Robot ID", "Robot Type", "Error JSON", "Time of Exception", "Time Handled", "Error Type", "Action"])

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

    def add_exception(self, robot_id, robot_type, error_json, exception_time, handled_time="N/A"):
        row_position = self.exception_table.rowCount()
        self.exception_table.insertRow(row_position)
        self.exception_table.setItem(row_position, 0, QTableWidgetItem(robot_id))
        self.exception_table.setItem(row_position, 1, QTableWidgetItem(robot_type))
        self.exception_table.setItem(row_position, 2, QTableWidgetItem(error_json))
        self.exception_table.setItem(row_position, 3, QTableWidgetItem(exception_time))
        self.exception_table.setItem(row_position, 4, QTableWidgetItem(handled_time))

        error_type_box = QLineEdit()
        self.exception_table.setCellWidget(row_position, 5, error_type_box)

        mark_complete_button = QPushButton("Mark Complete")
        mark_complete_button.clicked.connect(lambda: self.mark_as_done(row_position))
        self.exception_table.setCellWidget(row_position, 6, mark_complete_button)

        self.log_exception(robot_id, robot_type, error_json, exception_time, handled_time)

    def mark_as_done(self, row):
        self.exception_table.removeRow(row)

    def log_exception(self, robot_id, robot_type, error_json, exception_time, handled_time):
        with open(log_file_path, "a") as log_file:
            log_file.write(f"{robot_id}, {robot_type}, {error_json}, {exception_time}, {handled_time}\n")

    def closeEvent(self, event):
        self.monitor_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotMonitorApp()
    window.show()
    sys.exit(app.exec_())
