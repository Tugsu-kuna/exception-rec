from PyQt5.QtGui import QTextItem
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, \
    QMessageBox, QMessageBox, QComboBox, QLineEdit
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
        self.exception_table.setColumnCount(12)
        self.exception_table.setColumnCount(12)
        self.exception_table.setHorizontalHeaderLabels(
            ["Robot ID", "Robot Type", "Error JSON", "Time of Exception", "Time Handled", "Error Type","Issue type","Problem Phenomenon ","Problem Location","Issue description","Handling Measures","Action"]
        )
             # Issue type - 7, Problem phenomenon -8 , Problem location -9, Issue description -10, Handling measures - 11
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
            issue_type_combo = QComboBox()
            issue_type_combo.addItems(["施工Construction", "设备Equipment", "系统System", "环境Environment", "客户Customer","接口Interface","操作Operation","网络Network","未知Unknown","设计Design"])
            self.exception_table.setCellWidget(row_position, 6, issue_type_combo)
            phenomenom_combo = QComboBox()
            phenomenom_combo.addItems(["取放货异常Abnormal pick-up and delivery","避障Obstacle avoidance","货叉检测无容器Forklift detection without container","识别不到地面码DM Code Error"
                                    ,"结构件损坏Structural damage"
                                    ,"行走异常Unable to drive"
                                    ,"网络通讯异常Network communication abnormality"
                                    ,"掉箱子或掉落件Drop Box or items"
                                    ,"卡箱异常Box stuck"
                                    ,"撞货架Collision with Shelf"
                                    ,"充电异常Abnormal charging"
                                    ,"设备异响Equipment abnormal sound"
                                    ,"数据错误data error"
                                    ,"输送线读码器扫码异常"
                                    ,"机器人安全装置触发Robot safety device triggered"
                                    ,"安全门装置触发Safety door device activated"
                                    ,"机器人相互碰撞 Two robots collide"])
            self.exception_table.setCellWidget(row_position, 7, phenomenom_combo)
            problem_location_combo = QComboBox()
            problem_location_combo.addItems(["漏装跨梁 Cross beam missed"
                                            ,"跨梁凸起 Cross beam"
                                            ,"货架码破损 Shelf code breakage"
                                            ,"货架码脱落 Shelf code falling off"
                                            ,"货架码翘边 Shelf code warping"
                                            ,"货架码脏污 Shelf code dirty"
                                            ,"缓存库位超高 Cache location is super high"
                                            ,"缓存库位超低 Cache bit ultralow"
                                            ,"划线精度偏差 Line drawing accuracy deviation"
                                            ,"地面码贴歪 Ground yard sticking crooked"
                                            ,"地面码脏污 Ground code dirty"
                                            ,"地面码破损 Ground code breakage"
                                            ,"地面码白点Ground code white dot"
                                            ,"地面码缺失 Ground code missing"
                                            ,"地脚定位偏差 Ground positioning deviation"
                                            ,"梳齿高度偏差 Deviation of comb height"
                                            ,"急停按钮损坏 Emergency stop button is damaged"
                                            ,"程序逻辑BUG Program logic bug"
                                            ,"版本更新问题 Version update issue"
                                            ,"对射光电偏移 Counter-photoelectric shift"
                                            ,"对射光电污损 Optical fouling"
                                            ,"五色灯异常 Abnormal five-color light"
                                            ,"小车光电异常 Car photoelectric anomaly"
                                            ,"播种架按钮异常 Seed rack button abnormality"
                                            ,"小车卡料 Box card master"
                                            ,"异常无法恢复 Abnormal cannot be recovered"
                                            ,"硬件损坏 Hardware damage"
                                            ,"底盘相机故障 Chassis camera malfunction"
                                            ,"货叉手指故障 Fork finger failure"
                                            ,"参数配置错误 Parameter configuration error"
                                            ,"对射光电异常 Optoelectronic anomaly"
                                            ,"货叉相机异常 Fork camera abnormal"
                                            ,"3D相机参数配置不准 3D camera parameter configuration is inaccurate"
                                            ,"背撑机构异常 Abnormality of back support mechanism"
                                            ,"钩子光电异常 Hook photoelectric anomaly"
                                            ,"把手、急停开关损坏 Handle, emergency stop switch damaged"
                                            ,"底盘相机故障 Chassis camera malfunction"
                                            ,"举升机构异常 Abnormal lifting mechanism"
                                            ,"驱动组件异常 Driver component exception"
                                            ,"万向轮连杆变形 Deformation of universal wheel connecting rod"
                                            ,"触边条损坏 Contact strip damage"
                                            ,"急停开关损坏 Emergency stop switch is damaged"
                                            ,"料箱检测光电异常 Material tank detection photoelectric anomaly"
                                            ,"地缝影响 Ground seam effect"
                                            ,"地面不平 Uneven ground"
                                            ,"地面异物Foreign objects on the ground"
                                            ,"网络掉线 Network disconnection"
                                            ,"物料超高 Material super high"
                                            ,"料箱多码 Tank multicode"
                                            ,"箱码损坏 Box code damage"
                                            ,"操作不规范 Irregular operation"
                                            ,"无法定义异常Problom Cannot located"
                                            ,"料箱异物 Debris on Box"
                                            ,"账物不一致Accounts and items are inconsistent"
                                            ,"取放箱位置错误Wrong pick and place box position"
                                            ,"举升高度误差Lifting height error"
                                            ,"箱子码歪或无码The box code is skewed or missing"
                                            ,"输送线读码器故障Conveyor line code reader malfunction"])
            self.exception_table.setCellWidget(row_position, 8, problem_location_combo)
            # Column 9: Issue Description
            issue_description_input = QLineEdit()
            self.exception_table.setCellWidget(row_position, 9, issue_description_input)

            # Column 10: Handling Measures
            handling_measures_input = QLineEdit()
            self.exception_table.setCellWidget(row_position, 10, handling_measures_input)
            mark_complete_button = QPushButton("Mark Complete")
            mark_complete_button.clicked.connect(lambda _, btn=mark_complete_button: self.mark_as_done(btn))
            self.exception_table.setCellWidget(row_position, 11, mark_complete_button)

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
            issue_type = self.exception_table.cellWidget(row, 6).currentText()
            phenomenon = self.exception_table.cellWidget(row, 7).currentText()
            problem_location = self.exception_table.cellWidget(row, 8).currentText()
            issue_description = self.exception_table.cellWidget(row, 9).text()
            handling_measures = self.exception_table.cellWidget(row, 10).text()
            self.completed_table.setItem(completed_row, 6, QTableWidgetItem(issue_type))
            self.completed_table.setItem(completed_row, 7, QTableWidgetItem(phenomenon))
            self.completed_table.setItem(completed_row, 8, QTableWidgetItem(problem_location))
            self.completed_table.setItem(completed_row, 9, QTableWidgetItem(issue_description))
            self.completed_table.setItem(completed_row, 10, QTableWidgetItem(handling_measures))

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
                "employee": self.session["employee"],
                "issue_type": issue_type,
                "problem_phenomenon": phenomenon,
                "problem_location": problem_location,
                "issue_description": issue_description,
                "handling_measures": handling_measures,
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
        self.completed_table.setColumnCount(11)
        self.completed_table.setHorizontalHeaderLabels([
            "Robot ID", "Robot Type", "Error JSON", "Time of Exception", "Time Handled", "Error Type",
            "Issue Type", "Problem Phenomenon", "Problem Location", "Issue Description", "Handling Measures"
        ])

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
            self.completed_table.setItem(row, 6, QTableWidgetItem(str(record.get("issue_type", ""))))
            self.completed_table.setItem(row, 7, QTableWidgetItem(str(record.get("problem_phenomenon", ""))))
            self.completed_table.setItem(row, 8, QTableWidgetItem(str(record.get("problem_location", ""))))
            self.completed_table.setItem(row, 9, QTableWidgetItem(str(record.get("issue_description", ""))))
            self.completed_table.setItem(row, 10, QTableWidgetItem(str(record.get("handling_measures", ""))))

            self.completed_table.resizeColumnsToContents()

    def closeEvent(self, event):
        self.monitor_thread.stop()
        event.accept()