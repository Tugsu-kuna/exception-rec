from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QListWidget, QTableWidget, \
    QTableWidgetItem, QPushButton, QHBoxLayout
import sys

#  New imoprts by Kolomiiets Dmytro
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QHeaderView
#########################################################

class RobotMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window ico path
        icon_path = os.path.join(os.path.dirname(__file__), "ico", "icon.ico")


        # Set new icon to window
        self.setWindowIcon(QIcon(icon_path))

        self.setWindowTitle("Robot Monitoring System")
        self.setGeometry(100, 100, 1270, 720)

        self.initUI()

    def initUI(self):
        self.tabs = QTabWidget()

        # Buttons ico paths
        monitoring_ico_path     = os.path.join(os.path.dirname(__file__), "ico", "monitoring.svg")
        exception_ico_path      = os.path.join(os.path.dirname(__file__), "ico", "filter.svg")
        workflow_ico_path       = os.path.join(os.path.dirname(__file__), "ico", "view.svg")

        self.monitoring_tab = self.create_monitoring_tab()
        self.exception_handling_tab = self.create_exception_handling_tab()
        self.workflow_tab = QWidget()


        self.tabs.addTab(self.monitoring_tab, QIcon(monitoring_ico_path), "Monitoring")
        self.tabs.addTab(self.exception_handling_tab, QIcon(exception_ico_path), "Exception Handling")
        self.tabs.addTab(self.workflow_tab, QIcon(workflow_ico_path), "Workflow")


        # Added shadow on some elements 
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(3, 3)

        self.tabs.setGraphicsEffect(shadow)
        ###########################################################

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

        # Add frame if you no need you can remove it
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)
        frame.setLineWidth(2)
        layout.addWidget(frame)

        # Create Table for data
        self.exception_table = QTableWidget()
        self.exception_table.setColumnCount(5)
        self.exception_table.setHorizontalHeaderLabels(
            ["Robot ID", "Error Type", "Time of Exception", "Time Handled", "Comment"])

        # Set automaticly columns width
        header = self.exception_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents + 20)  # Just for check will be better to change on Stretch
        header.setSectionResizeMode(1, QHeaderView.Stretch)           
        header.setSectionResizeMode(2, QHeaderView.Stretch)          
        header.setSectionResizeMode(3, QHeaderView.Stretch)           
        header.setSectionResizeMode(4, QHeaderView.Stretch)           

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
    font = QFont("Arial", 10)  # Could be changed on other any font

    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Set style type like default
    app.setFont(font)

    window = RobotMonitorApp()
    window.show()

    sys.exit(app.exec_())
