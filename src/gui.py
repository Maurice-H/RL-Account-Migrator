from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QTabWidget, QLabel, QFileDialog, QMessageBox, QApplication,
    QScrollArea, QFrame 
)
from pathlib import Path
from util import RLManager

# --- Helper Functions ---
def show_error(parent, message):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle("Error")
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()

def elide_path(path: str, max_len: int = 60) -> str:
    """Shorten long paths for display but keep full path in tooltip."""
    if not path:
        return "not selected"
    if len(path) <= max_len:
        return path
    head = path[: int(max_len * 0.45)]
    tail = path[-int(max_len * 0.45) :]
    return f"{head}…{tail}"

def card_frame_widget(title, description, notice_text=None):
    frame = QFrame()
    frame.setFrameShape(QFrame.StyledPanel)
    frame.setStyleSheet("background-color: #2a2a3d; border-radius: 12px; padding: 12px;")

    layout = QVBoxLayout(frame)
    layout.setSpacing(12)

    title_label = QLabel(title)
    title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
    layout.addWidget(title_label)

    desc_label = QLabel(description)
    desc_label.setWordWrap(True)
    desc_label.setStyleSheet("color: #cfcfdd; font-size: 14px;")
    layout.addWidget(desc_label)

    # Optional notice
    if notice_text:
        notice = QLabel(notice_text)
        notice.setWordWrap(True)
        notice.setAlignment(Qt.AlignCenter)
        notice.setStyleSheet("""
            background-color: rgba(255, 200, 0, 0.15);
            border: 1px solid rgba(255, 200, 0, 0.35);
            padding: 8px;
            border-radius: 8px;
            color: #ffe083;
            font-size: 14px;
            font-weight: 600;
        """)
        layout.addWidget(notice)

    return frame

# --- Base Tab Class ---
class RequiresSetupTab(QWidget):
    def __init__(self, rl_manager: RLManager):
        super().__init__()
        self.rl_manager = rl_manager

    def on_enter(self):
        """Called when the tab becomes active."""
        if hasattr(self, "check_for_set_up"):
            self.check_for_set_up()

# --- Main Window ---
class RLMainWindow(QMainWindow):
    def __init__(self, rl_manager: RLManager):
        super().__init__()
        self.setWindowTitle("RL Account Migrator")
        self.setMinimumSize(820, 600)
        self.rl_manager = rl_manager

        self.setIcons()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.home_tab = HomeTab(self.navigate_to_tab, self.rl_manager)
        self.setup_tab = DebugTab(self.rl_manager)
        self.migrate_tab = MigrateSettingsTab(self.rl_manager)

        self.tabs.addTab(self.home_tab, "Home")
        self.tabs.addTab(self.migrate_tab, "Migrate Settings")
        self.tabs.addTab(self.setup_tab, "Manual Setup")

        self.tabs.currentChanged.connect(self.on_tab_changed)

    def setIcons(self):
        base = Path(__file__).resolve().parent
        icon_path = base.parent / "assets" / "icons" / "app.ico"
        self.setWindowIcon(QIcon(str(icon_path)))

    def on_tab_changed(self, index: int):
        widget = self.tabs.widget(index)
        if hasattr(widget, "on_enter"):
            widget.on_enter()

    def navigate_to_tab(self, index: int):
        self.tabs.setCurrentIndex(index)

# --- Home Tab ---
class HomeTab(QWidget):
    def __init__(self, navigate_callback, rl_manager: RLManager):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(18)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        welcome = QLabel("RL Account Migrator")
        welcome.setStyleSheet("font-size: 20px; font-weight: 700; color: #ffffff;")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Skip intros and migrate settings between accounts.")
        subtitle.setStyleSheet("font-size: 13px; color: #cfcfe6;")
        subtitle.setWordWrap(True)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        setup_step_label = QLabel("Step 1\nGet Config paths")
        setup_step_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #e0e0f0;")
        setup_step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_setup = QPushButton("Get Config")
        btn_setup.setToolTip("Sets up needed paths for steam and epic")
        btn_setup.setFixedWidth(180)
        
        stats_dic = rl_manager.check_all_paths_set()
        self.setup_step_label = QLabel(stats_dic["text"], alignment=Qt.AlignmentFlag.AlignCenter)
        self.setup_step_label.setStyleSheet(f"color: {stats_dic["color"]};")

        get_save_grid = QGridLayout()
        get_save_grid.setHorizontalSpacing(12)
        get_save_grid.setVerticalSpacing(10)

        get_save_step_label = QLabel("Step 2\nLog in to Steam or Epic with your account and start the backup process.")
        get_save_step_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #e0e0f0;")
        get_save_step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        get_save_epic_label = QLabel("Epic", alignment=Qt.AlignmentFlag.AlignCenter)
        get_save_epic = QPushButton("Save Epic Settings")
        get_save_epic.setToolTip("Starts Rocket League to generate new save files for epic")
        get_save_epic.setFixedWidth(160)

        get_save_steam_label = QLabel("Steam", alignment=Qt.AlignmentFlag.AlignCenter)
        get_save_steam = QPushButton("Save Steam Settings")
        get_save_steam.setToolTip("Starts Rocket League to generate new save files for steam")
        get_save_steam.setFixedWidth(160)

        get_save_grid.addWidget(get_save_epic_label, 0, 0)
        get_save_grid.addWidget(get_save_epic, 1, 0)
        get_save_grid.addWidget(get_save_steam_label, 0, 1)
        get_save_grid.addWidget(get_save_steam, 1, 1)

        migrate_step_label = QLabel("Step 3\nNow you are ready to copy your settings to steam or epic.")
        migrate_step_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #e0e0f0;")
        migrate_step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_migrate = QPushButton("Migrate Settings")
        btn_migrate.setFixedWidth(160)

        migrate_box = QVBoxLayout()
        migrate_box.addWidget(migrate_step_label)
        migrate_box.addWidget(btn_migrate, alignment=Qt.AlignmentFlag.AlignCenter)
        migrate_box.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(welcome)
        layout.addWidget(subtitle)
        layout.addWidget(setup_step_label, alignment=Qt.AlignmentFlag.AlignCenter)        
        layout.addWidget(btn_setup, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.setup_step_label)
        layout.addWidget(get_save_step_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(get_save_grid)
        layout.addLayout(migrate_box)

        btn_setup.clicked.connect(lambda: self.run_auto_config(rl_manager))
        btn_migrate.clicked.connect(lambda: navigate_callback(1))
        get_save_epic.clicked.connect(lambda: rl_manager.generate_new_save_files("get_backup", "epic"))
        get_save_steam.clicked.connect(lambda: rl_manager.generate_new_save_files("get_backup", "steam"))

    def run_auto_config(self, rl_manager: RLManager):
        
        self.log_status(text="Starting auto config", color="#f0c36b")
        try:
            ok = rl_manager.get_rocket_league_locations()
            if bool(ok):
                self.log_status(text="Settings configured successfully!", color="#86d07f")
                QMessageBox.information(self, "Done", "Settings configured successfully.")
            else:
                self.log_status(text="Couldn't configured settings.\nVisit Manual Setup", color="#d97777")
                QMessageBox.information(self, "Info", "Couldn't configured settings.\nVisit Manual Setup")
        except Exception as e:
            self.log_status(text="Error occurred.", color="#d97777")
            show_error(self, str(e))

    def log_status(self, text: str = "", color: str = "#d0d0d8"):
        self.setup_step_label.setText(text)
        self.setup_step_label.setStyleSheet(f"color: {color};")


# --- Migrate Settings Tab ---
class MigrateSettingsTab(RequiresSetupTab):
    def __init__(self, rl_manager: RLManager):
        super().__init__(rl_manager)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll.setWidget(container)
        main = QVBoxLayout(container)
        main.setContentsMargins(18,18,18,18)
        main.setSpacing(12)
        main.setAlignment(Qt.AlignmentFlag.AlignTop)

        instr_card = card_frame_widget(
            "Migrate Settings & Skip Intro",
            "Copy settings from your primary account saves to the new account."
        )
        main.addWidget(instr_card)
        
        migrate_grid = QGridLayout()
        migrate_grid.setHorizontalSpacing(12)
        migrate_grid.setVerticalSpacing(10)

        migrate_header_epic = QLabel("Epic", alignment=Qt.AlignmentFlag.AlignCenter)
        self.btn_migrate_epic = QPushButton("Migrate to current epic account")

        self.status_label_epic = QLabel("Epic status: -", alignment=Qt.AlignmentFlag.AlignCenter)
        self.status_label_epic.setStyleSheet("color: #d0d0d8;")

        migrate_grid.addWidget(migrate_header_epic, 0, 0)
        migrate_grid.addWidget(self.btn_migrate_epic, 1, 0)
        migrate_grid.addWidget(self.status_label_epic, 2, 0)

        migrate_header_steam = QLabel("Steam", alignment=Qt.AlignmentFlag.AlignCenter)
        self.btn_migrate_steam = QPushButton("Migrate to current steam account")

        self.status_label_steam = QLabel("Steam status: -", alignment=Qt.AlignmentFlag.AlignCenter)
        self.status_label_steam.setStyleSheet("color: #d0d0d8;")

        migrate_grid.addWidget(migrate_header_steam, 0, 1)
        migrate_grid.addWidget(self.btn_migrate_steam, 1, 1)
        migrate_grid.addWidget(self.status_label_steam, 2, 1)

        migrate_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main.addLayout(migrate_grid)

        outer = QVBoxLayout(self)
        outer.addWidget(scroll)

        self.btn_migrate_epic.clicked.connect(lambda: self.run_migration(platform="epic"))
        self.btn_migrate_steam.clicked.connect(lambda: self.run_migration(platform="steam"))
        self.check_for_set_up()

    def check_for_set_up(self):
        ready_epic = bool(self.rl_manager.save_path_epic and self.rl_manager.rocket_league_path_epic)
        ready_steam = bool(self.rl_manager.save_path_steam and self.rl_manager.rocket_league_path_steam)
        self.btn_migrate_steam.setEnabled(ready_steam)
        self.btn_migrate_epic.setEnabled(ready_epic)
        if not ready_epic:
            self.status_label_epic.setText("Status: \nPlease repeat get config at home tab\n or \nvisit Manual Setup tab.")
            self.status_label_epic.setStyleSheet("color: #f0b36b;")
        elif ready_epic:
            self.status_label_epic.setText("Status: Ready")
            self.status_label_epic.setStyleSheet("color: #86d07f;")

        if not ready_steam:
            self.status_label_steam.setText("Status: \nPlease repeat get config at home tab\n or \nvisit Manual Setup tab.")
            self.status_label_steam.setStyleSheet("color: #f0b36b;")
        elif ready_steam:
            self.status_label_steam.setText("Status: Ready")
            self.status_label_steam.setStyleSheet("color: #86d07f;")

    def log_status(self, platform: str = "steam" or "epic", text: str = "", color: str = "#d0d0d8"):
        if platform == "steam":
            self.status_label_steam.setText(text)
            self.status_label_steam.setStyleSheet(f"color: {color};")
        elif platform == "epic":
            self.status_label_epic.setText(text)
            self.status_label_epic.setStyleSheet(f"color: {color};") 
        
        QApplication.processEvents()

    def run_migration(self, platform: str = "steam" or "epic"):
        err = self.rl_manager.check_folder_paths_set(platform=platform)
        err2 = self.rl_manager.check_backup_folder_empty()
        if err:
            show_error(self, err)
            return
        if err2:
            show_error(self, err2)
            return
        self.log_status(platform=platform, text="Starting Rocket League and waiting for new save files...", color="#f0c36b")
        try:
            ok = self.rl_manager.generate_new_save_files(mode="replace_existing", platform=platform)
            if ok:
                self.log_status(platform=platform, text="Settings migrated successfully!", color="#86d07f")
                QMessageBox.information(self, "Done", "Settings migrated successfully.")
            else:
                self.log_status(platform=platform, text="No saves found to migrate.", color="#d97777")
                QMessageBox.information(self, "Info", "No saves found to migrate.")
        except Exception as e:
            self.log_status(platform=platform, text="Error occurred.", color="#d97777")
            show_error(self, str(e))

# --- Setup Tab ---
class DebugTab(RequiresSetupTab):
    def __init__(self, rl_manager: RLManager):
        super().__init__(rl_manager)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        scroll.setWidget(container)

        main = QVBoxLayout(container)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)
        main.setAlignment(Qt.AlignmentFlag.AlignTop)

        instr_card = card_frame_widget(
        "Manual Setup",
        "Select the Steam and/or Epic Games DBE_Production folders and exe files for Rocket League",
        notice_text="Manuel setup is only needed if automatic detection fails."
        )   
        main.addWidget(instr_card)

        self.save_label_epic = QLabel(f"Epic DBE_Production folder: {elide_path(rl_manager.save_path_epic)}")
        self.save_label_epic.setToolTip(rl_manager.save_path_epic or "")
        self.save_label_epic.setWordWrap(True)
        self.save_label_steam = QLabel(f"Steam DBE_Production folder: {elide_path(rl_manager.save_path_steam)}")
        self.save_label_steam.setToolTip(rl_manager.save_path_steam or "")
        self.save_label_steam.setWordWrap(True)
        
        self.save_info = QLabel("Default DBE_Production paths \nSteam: C:/Users/<you>/Documents/My Games/Rocket League/TAGame/SaveData/DBE_Production  \nEpic: same to TAGame/SaveDataEpic/DBE_Production")
        self.save_info.setStyleSheet("color: #bfbfcf; font-size: 12px;")

        self.backup_label = QLabel(f"Backup file locations: {elide_path(rl_manager.backup_path)}")
        self.backup_label.setToolTip(rl_manager.backup_path or "")
        self.backup_label.setWordWrap(True)

        self.exe_label_epic = QLabel(f"Epic Rocket League exe: {elide_path(rl_manager.rocket_league_path_epic)}")
        self.exe_label_epic.setToolTip(rl_manager.rocket_league_path_epic or "")
        self.exe_label_epic.setWordWrap(True)
        self.exe_label_steam = QLabel(f"Steam Rocket League exe: {elide_path(rl_manager.rocket_league_path_steam)}")
        self.exe_label_steam.setToolTip(rl_manager.rocket_league_path_steam or "")
        self.exe_label_steam.setWordWrap(True)
        
        self.exe_info = QLabel("Default exe paths \nSteam: C:/Program Files (x86)/Steam/steamapps/common/rocketleague/Binaries/Win64/RocketLeague.exe  \nEpic: C:/Program Files/Epic Games/rocketleague/Binaries/Win64/RocketLeague.exe")
        self.exe_info.setStyleSheet("color: #bfbfcf; font-size: 12px;")
        
        self.status_label_epic = QLabel("Epic status: ‑")
        self.status_label_steam = QLabel("Steam status: ‑")

        main.addWidget(self.save_label_epic)
        main.addWidget(self.save_label_steam)
        main.addWidget(self.save_info)
        main.addWidget(self.exe_label_epic)
        main.addWidget(self.exe_label_steam)
        main.addWidget(self.exe_info)
        main.addWidget(self.backup_label)

        btn_grid = QGridLayout()
        btn_grid.setHorizontalSpacing(12)
        btn_grid.setVerticalSpacing(10)

        self.btn_choose_save_epic = QPushButton("Choose epic DBE_Production folder")
        self.btn_choose_save_steam = QPushButton("Choose steam DBE_Production folder")
        self.btn_choose_exe_epic = QPushButton("Choose epic Rocket League exe")
        self.btn_choose_exe_steam = QPushButton("Choose steam Rocket League exe")

        btn_grid.addWidget(self.btn_choose_save_epic, 0, 0)
        btn_grid.addWidget(self.btn_choose_save_steam, 0, 1)
        btn_grid.addWidget(self.btn_choose_exe_epic, 1, 0)
        btn_grid.addWidget(self.btn_choose_exe_steam, 1, 1)
        btn_grid.addWidget(self.status_label_steam, 2, 1)
        btn_grid.addWidget(self.status_label_epic, 2, 0)
        btn_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main.addLayout(btn_grid)

        outer = QVBoxLayout(self)
        outer.addWidget(scroll)

        self.btn_choose_save_epic.clicked.connect(lambda: self.choose_path("save_epic"))
        self.btn_choose_save_steam.clicked.connect(lambda: self.choose_path("save_steam"))
        self.btn_choose_exe_epic.clicked.connect(lambda: self.choose_path("rocket_league_epic"))
        self.btn_choose_exe_steam.clicked.connect(lambda: self.choose_path("rocket_league_steam"))
  
        self.check_for_set_up()
        
    
    def check_for_set_up(self):
        self.update_all_labels_and_status()

    def _style_status(self, state: str, label: str = "epic" or "steam"):
        color_map = {
            "ready": ("#dff7e0", "#2ca84a"),
            "warning": ("#fff6e0", "#b77b00"),
            "error": ("#ffe6e6", "#d02a2a"),
            "incomplete": ("#ededf5", "#7a7aa8")
        }
        bg, fg = color_map.get(state, color_map["incomplete"])
        if label == "epic":
            self.status_label_epic.setStyleSheet(
                f"background: {bg}; color: {fg}; border-radius: 8px; padding: 8px; font-weight: 600;"
            )
        elif label == "steam":
            self.status_label_steam.setStyleSheet(
                f"background: {bg}; color: {fg}; border-radius: 8px; padding: 8px; font-weight: 600;"
            )

    def update_all_labels_and_status(self):
        self.save_label_epic.setText(f"Epic DBE_Production folder: {elide_path(self.rl_manager.save_path_epic)}")
        self.save_label_epic.setToolTip(self.rl_manager.save_path_epic or "")
        self.save_label_steam.setText(f"Steam DBE_Production folder: {elide_path(self.rl_manager.save_path_steam)}")
        self.save_label_steam.setToolTip(self.rl_manager.save_path_steam or "")
        self.exe_label_epic.setText(f"Epic Rocket League exe: {elide_path(self.rl_manager.rocket_league_path_epic)}")
        self.exe_label_epic.setToolTip(self.rl_manager.rocket_league_path_epic or "")
        self.exe_label_steam.setText(f"Steam Rocket League exe: {elide_path(self.rl_manager.rocket_league_path_steam)}")
        self.exe_label_steam.setToolTip(self.rl_manager.rocket_league_path_steam or "")

        save_set_epic = bool(self.rl_manager.save_path_epic)
        exe_set_epic = bool(self.rl_manager.rocket_league_path_epic)
        save_set_steam = bool(self.rl_manager.save_path_steam)
        exe_set_steam = bool(self.rl_manager.rocket_league_path_steam)

        if not (save_set_steam or exe_set_steam):
            self.status_label_steam.setText("Steam status: Please configure save & exe path.")
            self._style_status("incomplete", "steam")
        elif not save_set_steam and exe_set_steam:
            self.status_label_steam.setText("Steam status: DBE_Production folder missing.")
            self._style_status("warning", "steam")
        elif save_set_steam and not exe_set_steam:
            self.status_label_steam.setText("Steam status: Rocket League exe missing.")
            self._style_status("warning", "steam")
        else:
            self.status_label_steam.setText("Steam status: Ready")
            self._style_status("ready", "steam")

        if not (save_set_epic or exe_set_epic):
            self.status_label_epic.setText("Epic status: Please configure save & exe path.")
            self._style_status("incomplete", "epic")
        elif not save_set_epic and exe_set_epic:
            self.status_label_epic.setText("Epic status: DBE_Production folder missing.")
            self._style_status("warning", "epic")
        elif save_set_epic and not exe_set_epic:
            self.status_label_epic.setText("Epic status: Rocket League exe missing.")
            self._style_status("warning", "epic")
        else:
            self.status_label_epic.setText("Epic status: Ready")
            self._style_status("ready", "epic")

        win = self.window()
        if hasattr(win, "tabs"):
            for i in range(win.tabs.count()):
                w = win.tabs.widget(i)
                if hasattr(w, "check_for_set_up"):
                    try:
                        w.check_for_set_up()
                    except Exception:
                        pass

    def choose_path(self, folder_type: str):
        settings = self.rl_manager.settings
        if folder_type == "rocket_league_epic" or folder_type == "rocket_league_steam":
            path, _ = QFileDialog.getOpenFileName(self, "Select Rocket League exe", "", "Executables (*.exe)")
            if path:
                if folder_type == "rocket_league_epic":
                    self.rl_manager.rocket_league_path_epic = path
                    settings.setValue("rocket_league_path_epic", path)
                elif folder_type == "rocket_league_steam":
                    self.rl_manager.rocket_league_path_steam = path
                    settings.setValue("rocket_league_path_steam", path)
        else:
            folder = QFileDialog.getExistingDirectory(self, f"Choose {folder_type} folder")
            if folder:
                if folder_type == "save_epic" or folder_type == "save_steam":
                    if folder_type == "save_epic":
                        self.rl_manager.save_path_epic = folder
                        err = self.rl_manager.check_folders_identical(platform="epic")
                        err2 = self.rl_manager.check_path_contains_save_files(platform="epic")
                        if err:
                            self.rl_manager.save_path_epic = ""
                            show_error(self, err)
                        elif err2:
                            self.rl_manager.save_path_epic = ""
                            show_error(self, err2)
                        settings.setValue("save_path_epic", self.rl_manager.save_path_epic)
                    elif folder_type == "save_steam":
                        self.rl_manager.save_path_steam = folder
                        err = self.rl_manager.check_folders_identical(platform="steam")
                        err2 = self.rl_manager.check_path_contains_save_files(platform="steam")
                        if err:
                            self.rl_manager.save_path_steam = ""
                            show_error(self, err)
                        elif err2:
                            self.rl_manager.save_path_steam = ""
                            show_error(self, err2)
                        settings.setValue("save_path_steam", self.rl_manager.save_path_steam)

        self.update_all_labels_and_status()