Repo structure

exception-rec/warecode
│
├── GUI_Script.py                # entry point, starts the app
├── ui/
│   ├── __init__.py
│   ├── main_window.py     # QMainWindow, tabs, layout
│   ├── blacklist_tab.py   # GUI for blacklist management
│   └── exception_tab.py   # GUI for exception handling
│
├── core/
│   ├── __init__.py
│   ├── monitor_thread.py  # RobotMonitorThread class
│   ├── blacklist.py       # load/save/check blacklist
│   └── reporting.py       # export to CSV/Excel
│
├── resources/
│   ├── blacklist.json     # your ranges
│   └── icons/             # any images/icons
│
└── misc

