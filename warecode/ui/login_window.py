from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from core.session import start_session

class LoginWindow(QWidget):
    def __init__(self, on_login, parent=None):
        super().__init__(parent)
        self.on_login = on_login
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.label = QLabel("Enter your name to start session:")
        self.name_input = QLineEdit()
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)

        layout.addWidget(self.label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.login_btn)
        self.setLayout(layout)

    def handle_login(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Name cannot be empty.")
            return
        session = start_session(name)
        self.on_login(session)
