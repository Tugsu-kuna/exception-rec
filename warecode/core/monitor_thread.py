import time, json, requests
from PyQt5.QtCore import QThread, pyqtSignal
from .blacklist import load_blacklist, is_blacklisted

ess_ip = 'http://10.251.3.24:9000/'
query_type_url = ess_ip + 'ess-api/model/queryModelByType?modelType=robot'
headers = {'Content-Type': 'application/json', 'accept': 'application/json'}

class RobotMonitorThread(QThread):
    update_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str, str, str, str, str, str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.error_logs = {}
        self.handled_robots = set()
        self.blacklist_ranges = load_blacklist()

    def mark_robot_handled(self, robot_name):
        self.handled_robots.add(robot_name)
        if robot_name in self.error_logs:
            del self.error_logs[robot_name]

    def run(self):
        while self.running:
            try:
                response = requests.get(query_type_url, headers=headers, timeout=1)
                if response.status_code != 200:
                    time.sleep(1)
                    continue

                result = response.json()
                if 'data' not in result or 'robot' not in result['data']:
                    time.sleep(1)
                    continue

                robots = result['data']['robot']
                robot_data = []
                for robot in robots:
                    name = robot.get('code', 'Unknown Robot')
                    if is_blacklisted(name, self.blacklist_ranges):
                        continue

                    state = robot.get('hardwareState', 'UNKNOWN')
                    robot_type = robot.get('robotTypeCode', 'UNKNOWN')
                    error_info = robot.get('otherHardwareInfo', {}).get('errorState', [])

                    if robot_type == "RT_KUBOT":
                        display_type = "Big Robot"
                    elif robot_type == "RT_KUBOT_MINI_HAIFLEX":
                        display_type = "Small Robot"
                    else:
                        display_type = "Unknown Type"

                    robot_data.append((name, display_type, state))

                    if name in self.handled_robots and state == "ROBOT_ABNORMAL":
                        continue  # <--- NEW: Skip robots that user handled manually

                    # Device exception
                    if state == "ROBOT_ABNORMAL" and error_info:
                        error_json = json.dumps(error_info, indent=2)
                        if name not in self.error_logs:
                            start_time = time.strftime("%Y-%m-%d %H:%M:%S")
                            self.error_logs[name] = start_time
                            self.error_signal.emit(name, display_type, error_json, start_time, "N/A",
                                                   "Device Exception")

                    # System exception (command timeout)
                    elif robot.get("isCommandTimeout", False):
                        if name not in self.error_logs:
                            start_time = time.strftime("%Y-%m-%d %H:%M:%S")
                            self.error_logs[name] = start_time
                            self.error_signal.emit(name, display_type, "Command Timeout", start_time, "N/A",
                                                   "System Exception")

                    # Resolution
                    elif name in self.error_logs:
                        handled_time = time.strftime("%Y-%m-%d %H:%M:%S")
                        self.error_signal.emit(name, display_type, "Resolved", self.error_logs[name], handled_time,
                                               "Resolved")
                        del self.error_logs[name]
                self.update_signal.emit(robot_data)
            except Exception as e:
                print(f"🚨 Error: {str(e)}")
            time.sleep(1)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
