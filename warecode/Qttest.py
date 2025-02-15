import sys
import requests
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout

ess_ip = 'http://10.251.3.25:9000/'
query_type_url = ess_ip + 'ess-api/model/queryModelByType?modelType=robot'
headers = {'Content-Type': 'application/json', 'accept': 'application/json'}

class RobotMonitorThread(QThread):
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

