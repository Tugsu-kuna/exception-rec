import sys
import requests
import time
import os
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QTableWidget, \
    QTableWidgetItem, QPushButton, QHBoxLayout

# ESS API URL and Headers for Robot Status
ess_ip = 'http://10.251.3.25:9000/'
query_type_url = ess_ip + 'ess-api/model/queryModelByType?modelType=robot'
headers = {'Content-Type': 'application/json', 'accept': 'application/json'}

# Log file path
log_file_path = "D:\\Project\\warecode\\exception.txt"


# The Robot Monitor Thread that checks the robot states every 1 second
class RobotMonitorThread(QThread):
    update_signal = pyqtSignal(list)  # Signal to update the monitoring tab
    error_signal = pyqtSignal(str, str, str, str)  # (Robot Name, Error Message, Start Time, Handled Time)

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
                    robot_data.append((name, state))
                    error_info = robot.get('otherHardwareInfo', {}).get('errorState', [])

                    if state == "ROBOT_ABNORMAL" and error_info:
                        error_texts = list(set([err["info"] for err in error_info]))
                        error_message = "\n".join(error_texts)
                        if name not in self.error_logs:
                            start_time = time.strftime("%Y-%m-%d %H:%M:%S")
                            self.error_logs[name] = start_time
                            self.error_signal.emit(name, error_message, start_time, "N/A")

                    elif name in self.error_logs:
                        handled_time = time.strftime("%Y-%m-%d %H:%M:%S")
                        self.error_signal.emit(name, "Resolved", self.error_logs[name], handled_time)
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
        self.setGeometry(100, 100, 800, 600)

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
        self.robot_table.setColumnCount(2)
        self.robot_table.setHorizontalHeaderLabels(["Robot ID", "State"])
        layout.addWidget(self.robot_table)

        tab.setLayout(layout)
        return tab

    def create_exception_handling_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.exception_table = QTableWidget()
        self.exception_table.setColumnCount(6)
        self.exception_table.setHorizontalHeaderLabels(
            ["Robot ID", "Error Type", "Time of Exception", "Time Handled", "Comment", "Action"])

        layout.addWidget(self.exception_table)
        tab.setLayout(layout)
        return tab

    def update_monitoring_tab(self, robot_data):
        self.robot_table.setRowCount(0)
        for row_index, (robot_id, state) in enumerate(robot_data):
            self.robot_table.insertRow(row_index)
            self.robot_table.setItem(row_index, 0, QTableWidgetItem(robot_id))
            self.robot_table.setItem(row_index, 1, QTableWidgetItem(state))

    def add_exception(self, robot_id, error_type, exception_time, handled_time="N/A", comment="N/A"):
        row_position = self.exception_table.rowCount()
        self.exception_table.insertRow(row_position)

        self.exception_table.setItem(row_position, 0, QTableWidgetItem(robot_id))
        self.exception_table.setItem(row_position, 1, QTableWidgetItem(error_type))
        self.exception_table.setItem(row_position, 2, QTableWidgetItem(exception_time))
        self.exception_table.setItem(row_position, 3, QTableWidgetItem(handled_time))
        self.exception_table.setItem(row_position, 4, QTableWidgetItem(comment))

        mark_complete_button = QPushButton("Mark Complete")
        mark_complete_button.clicked.connect(lambda: self.mark_as_done(row_position))
        self.exception_table.setCellWidget(row_position, 5, mark_complete_button)

        self.log_exception(robot_id, error_type, exception_time, handled_time, comment)

    def mark_as_done(self, row):
        self.exception_table.removeRow(row)

    def log_exception(self, robot_id, error_type, exception_time, handled_time, comment):
        with open(log_file_path, "a") as log_file:
            log_file.write(f"{robot_id}, {error_type}, {exception_time}, {handled_time}, {comment}\n")

    def closeEvent(self, event):
        self.monitor_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotMonitorApp()
    window.show()
    sys.exit(app.exec_())
