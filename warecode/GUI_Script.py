import sys
import requests
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QListWidget, QTableWidget, \
    QTableWidgetItem, QPushButton, QHBoxLayout

# ESS API URL and Headers for Robot Status
ess_ip = 'http://10.251.3.25:9000/'
query_type_url = ess_ip + 'ess-api/model/queryModelByType?modelType=robot'
headers = {'Content-Type': 'application/json', 'accept': 'application/json'}


# The Robot Monitor Thread that checks the robot states every 1 second
class RobotMonitorThread(QThread):
    # Signal to update the main GUI with the robot error states
    error_signal = pyqtSignal(str, str, str)  # (Robot Name, Error Message, Start Time)

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
                for robot in robots:
                    name = robot.get('code', 'Unknown Robot')
                    state = robot.get('hardwareState', 'UNKNOWN')
                    error_info = robot.get('otherHardwareInfo', {}).get('errorState', [])

                    # If robot is abnormal and has an error
                    if state == "ROBOT_ABNORMAL" and error_info:
                        error_texts = list(set([err["info"] for err in error_info]))  # Remove duplicates
                        error_message = "\n".join(error_texts)

                        # Emit signal to the main thread to update the GUI
                        if name not in self.error_logs:
                            start_time = time.strftime("%Y-%m-%d %H:%M:%S")
                            self.error_logs[name] = start_time
                            self.error_signal.emit(name, error_message, start_time)

            except Exception as e:
                print(f"🚨 Error: {str(e)}")

            time.sleep(1)  # Prevent CPU overload

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


# Main Window of the Robot Monitoring System
class RobotMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robot Monitoring System")
        self.setGeometry(100, 100, 800, 600)

        self.initUI()

        # Start the robot monitor thread to check robot statuses
        self.monitor_thread = RobotMonitorThread()
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

    def add_exception(self, robot_id, error_type, exception_time, handled_time=None, comment=None):
        # Add a new row to the exception table
        row_position = self.exception_table.rowCount()
        self.exception_table.insertRow(row_position)

        self.exception_table.setItem(row_position, 0, QTableWidgetItem(robot_id))
        self.exception_table.setItem(row_position, 1, QTableWidgetItem(error_type))
        self.exception_table.setItem(row_position, 2, QTableWidgetItem(exception_time))
        self.exception_table.setItem(row_position, 3, QTableWidgetItem(handled_time if handled_time else "N/A"))
        self.exception_table.setItem(row_position, 4, QTableWidgetItem(comment if comment else "N/A"))

        # Create the "Mark Complete" button to remove the exception once handled
        mark_complete_button = QPushButton("Mark Complete")
        mark_complete_button.clicked.connect(lambda: self.mark_as_done(row_position))
        self.exception_table.setCellWidget(row_position, 5, mark_complete_button)

    def mark_as_done(self, row):
        robot_id = self.exception_table.item(row, 0).text()
        error_type = self.exception_table.item(row, 1).text()
        exception_time = self.exception_table.item(row, 2).text()

        # Here, you could save the completed exception to a file, database, or online sheet.
        print(f"Marking as done: {robot_id}, {error_type}, {exception_time}")

        self.exception_table.removeRow(row)

    def closeEvent(self, event):
        # Stop the monitoring thread when closing the app
        self.monitor_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotMonitorApp()
    window.show()
    sys.exit(app.exec_())
