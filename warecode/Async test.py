import sys
import requests
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout

class RobotMonitorThread(QThread):
    dataFetched = pyqtSignal(dict)
    error_signal = pyqtSignal(str, str, str)  # name, error_message, start_time

    def __init__(self, parent=None):
        super(RobotMonitorThread, self).__init__(parent)
        self.running = True

    def run(self):
        ess_ip = 'http://10.251.3.24eq:9000/'
        query_type_url = ess_ip + 'ess-api/model/queryModelByType?modelType=robot'
        headers = {'Content-Type': 'application/json', 'accept': 'application/json'}

        while self.running:
            try:
                response = requests.get(query_type_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    result = response.json()
                    robots = result.get('data', {}).get('robot', [])

                    for robot in robots:
                        state = robot.get('state', 'UNKNOWN')
                        hardware_state = robot.get('hardwareState', 'UNKNOWN')

                        if hardware_state == "ROBOT_ABNORMAL" or state == "ERROR":
                            name = robot.get('code', 'Unknown')
                            error_message = f"{state}, {hardware_state}"
                            start_time = time.strftime("%Y-%m-%d %H:%M:%S")
                            self.error_signal.emit(name, error_message, start_time)

                        self.dataFetched.emit(robot)
                else:
                    print("Error fetching data:", response.status_code)
            except requests.RequestException as e:
                print("Request failed:", e)

            time.sleep(1)


    def stop(self):
        self.running = False
        self.quit()
        self.wait()
class RobotMonitorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.monitor_thread = RobotMonitorThread()
        self.monitor_thread.error_signal.connect(self.show_error)
        self.monitor_thread.start()

    def initUI(self):
        self.setWindowTitle("Robot Monitor")
        self.setGeometry(100, 100, 400, 300)
        self.layout = QVBoxLayout()
        self.label = QLabel("Monitoring robots...")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def show_error(self, name, error_message, start_time):
        self.label.setText(f"⚠️ {name} ERROR!\n{error_message}\nStarted at: {start_time}")

    def closeEvent(self, event):
        self.monitor_thread.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RobotMonitorApp()
    window.show()
    sys.exit(app.exec_())