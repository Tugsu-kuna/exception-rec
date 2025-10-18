import sys
from PyQt5.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.main_window import RobotMonitorApp
from core.session import load_session

def main():
    app = QApplication(sys.argv)

    # Callback after login succeeds
    def launch_main(session):
        window = RobotMonitorApp(session)
        window.show()
        login.close()

    # If a session file already exists, load it and go straight to main
    saved = load_session()
    if saved:
        window = RobotMonitorApp(saved)
        window.show()
    else:
        login = LoginWindow(on_login=launch_main)
        login.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
