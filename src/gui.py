from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QTabWidget, QLabel, QFileDialog, QMessageBox, QApplication,
    QScrollArea, QFrame, QSystemTrayIcon 
)
import os
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
        self.setMinimumSize(720, 520)
        self.rl_manager = rl_manager

        self.setIcons()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.home_tab = HomeTab(self.navigate_to_tab)
        self.setup_tab = SetupTab(self.rl_manager)
        self.skip_tab = SkipIntroTab(self.rl_manager)
        self.migrate_tab = MigrateSettingsTab(self.rl_manager)

        self.tabs.addTab(self.home_tab, "Home")
        self.tabs.addTab(self.setup_tab, "Set Up")
        self.tabs.addTab(self.skip_tab, "Skip Intro")
        self.tabs.addTab(self.migrate_tab, "Migrate Settings")

        self.tabs.currentChanged.connect(self.on_tab_changed)

    def setIcons(self):
        app_icon = QIcon("assets/icons/app.ico")
        self.setWindowIcon(app_icon)

    def on_tab_changed(self, index: int):
        widget = self.tabs.widget(index)
        if hasattr(widget, "on_enter"):
            widget.on_enter()

    def navigate_to_tab(self, index: int):
        self.tabs.setCurrentIndex(index)

# --- Home Tab ---
class HomeTab(QWidget):
    def __init__(self, navigate_callback):
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

        btn_setup = QPushButton("Set Up")
        btn_setup.setToolTip("Choose save/backup folders and Rocket League exe")
        btn_setup.setFixedWidth(180)

        layout.addWidget(welcome)
        layout.addWidget(subtitle)
        layout.addWidget(btn_setup, alignment=Qt.AlignmentFlag.AlignCenter)

        layoutH = QHBoxLayout()
        layoutH.setSpacing(16)
        layoutH.addStretch()
        btn_skip = QPushButton("Skip Intro")
        btn_skip.setFixedWidth(160)
        btn_migrate = QPushButton("Migrate Settings")
        btn_migrate.setFixedWidth(160)
        layoutH.addWidget(btn_skip)
        layoutH.addWidget(btn_migrate)
        layoutH.addStretch()
        layout.addLayout(layoutH)

        btn_setup.clicked.connect(lambda: navigate_callback(1))
        btn_skip.clicked.connect(lambda: navigate_callback(2))
        btn_migrate.clicked.connect(lambda: navigate_callback(3))

# --- Setup Tab ---
class SetupTab(RequiresSetupTab):
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
        "Quick Setup",
        "Select the save folder of Rocket League, choose a backup folder to store your saved files, "
        "and point to the Rocket League executable. After setup you can run Skip Intro or Migrate Settings.",
        notice_text="Before creating any backups, start Rocket League once with the account you want to preserve.\n"
                    "This ensures the tool can detect and use the correct save files."
        )   
        main.addWidget(instr_card)

        self.save_label = QLabel(f"Save folder: {elide_path(rl_manager.save_path)}")
        self.save_label.setToolTip(rl_manager.save_path or "")
        self.save_label.setWordWrap(True)
        self.save_info = QLabel("Default path: C:/Users/<you>/Documents/My Games/Rocket League/TAGame/SaveDataEpic/DBE_Production")
        self.save_info.setStyleSheet("color: #bfbfcf; font-size: 12px;")

        self.backup_label = QLabel(f"Backup folder: {elide_path(rl_manager.backup_path)}")
        self.backup_label.setToolTip(rl_manager.backup_path or "")
        self.backup_label.setWordWrap(True)
        self.backup_info = QLabel("Folder where your save‑backups will be stored.")
        self.backup_info.setStyleSheet("color: #bfbfcf; font-size: 12px;")

        self.exe_label = QLabel(f"Rocket League exe: {elide_path(rl_manager.rocket_league_path)}")
        self.exe_label.setToolTip(rl_manager.rocket_league_path or "")
        self.exe_label.setWordWrap(True)
        self.exe_info = QLabel("Typical install path: C:/Program Files/Epic Games/rocketleague/Binaries/Win64")
        self.exe_info.setStyleSheet("color: #bfbfcf; font-size: 12px;")

        main.addWidget(self.save_label)
        main.addWidget(self.save_info)
        main.addWidget(self.backup_label)
        main.addWidget(self.backup_info)
        main.addWidget(self.exe_label)
        main.addWidget(self.exe_info)

        btn_grid = QGridLayout()
        btn_grid.setHorizontalSpacing(12)
        btn_grid.setVerticalSpacing(10)
        btn_width = 220

        self.btn_choose_save = QPushButton("Choose save folder")
        self.btn_unset_save = QPushButton("Unset save folder")
        self.btn_choose_backup = QPushButton("Choose backup folder")
        self.btn_unset_backup = QPushButton("Unset backup folder")
        self.btn_choose_exe = QPushButton("Choose Rocket League exe")
        self.btn_unset_exe = QPushButton("Unset Rocket League exe")

        for btn in [self.btn_choose_save, self.btn_unset_save,
                    self.btn_choose_backup, self.btn_unset_backup,
                    self.btn_choose_exe, self.btn_unset_exe]:
            btn.setFixedWidth(btn_width)

        btn_grid.addWidget(self.btn_choose_save, 0, 0)
        btn_grid.addWidget(self.btn_unset_save, 0, 1)
        btn_grid.addWidget(self.btn_choose_backup, 1, 0)
        btn_grid.addWidget(self.btn_unset_backup, 1, 1)
        btn_grid.addWidget(self.btn_choose_exe, 2, 0)
        btn_grid.addWidget(self.btn_unset_exe, 2, 1)

        main.addLayout(btn_grid)

        self.btn_store = QPushButton("Store latest .save as backup")
        self.btn_store.setFixedWidth(260)
        main.addWidget(self.btn_store, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("Status: ‑")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._style_status("incomplete")
        main.addWidget(self.status_label)

        outer = QVBoxLayout(self)
        outer.addWidget(scroll)

        self.btn_choose_save.clicked.connect(lambda: self.choose_folder("save"))
        self.btn_unset_save.clicked.connect(lambda: self.unset_folder("save"))
        self.btn_choose_backup.clicked.connect(lambda: self.choose_folder("backup"))
        self.btn_unset_backup.clicked.connect(lambda: self.unset_folder("backup"))
        self.btn_choose_exe.clicked.connect(lambda: self.choose_folder("rocket_league"))
        self.btn_unset_exe.clicked.connect(lambda: self.unset_folder("rocket_league"))
        self.btn_store.clicked.connect(lambda: self.store_latest_saves())

        self.update_all_labels_and_status()

    def _style_status(self, state: str):
        color_map = {
            "ready": ("#dff7e0", "#2ca84a"),
            "warning": ("#fff6e0", "#b77b00"),
            "error": ("#ffe6e6", "#d02a2a"),
            "incomplete": ("#ededf5", "#7a7aa8")
        }
        bg, fg = color_map.get(state, color_map["incomplete"])
        self.status_label.setStyleSheet(
            f"background: {bg}; color: {fg}; border-radius: 8px; padding: 8px; font-weight: 600;"
        )

    def update_all_labels_and_status(self):
        self.save_label.setText(f"Save folder: {elide_path(self.rl_manager.save_path)}")
        self.save_label.setToolTip(self.rl_manager.save_path or "")
        self.backup_label.setText(f"Backup folder: {elide_path(self.rl_manager.backup_path)}")
        self.backup_label.setToolTip(self.rl_manager.backup_path or "")
        self.exe_label.setText(f"Rocket League exe: {elide_path(self.rl_manager.rocket_league_path)}")
        self.exe_label.setToolTip(self.rl_manager.rocket_league_path or "")

        save_set = bool(self.rl_manager.save_path)
        backup_set = bool(self.rl_manager.backup_path)
        exe_set = bool(self.rl_manager.rocket_league_path)

        self.btn_store.setEnabled(save_set and backup_set)

        if not (save_set or backup_set or exe_set):
            self.status_label.setText("Status: Please configure save, backup & exe paths.")
            self._style_status("incomplete")
        elif not save_set and backup_set:
            self.status_label.setText("Status: Save folder missing.")
            self._style_status("warning")
        elif save_set and not backup_set:
            self.status_label.setText("Status: Backup folder missing.")
            self._style_status("warning")
        else:
            err = self.rl_manager.check_folders_identical()
            if err and self.rl_manager.save_path != "" and self.rl_manager.backup_path != "":
                self.status_label.setText(f"Status: {err}")
                self._style_status("error")
            else:
                err2 = self.rl_manager.check_path_contains_save_files()
                if err2:
                    self.status_label.setText(f"Status: {err2}")
                    self._style_status("warning")
                else:
                    if not exe_set:
                        self.status_label.setText("Status: Ready (exe missing)")
                        self._style_status("warning")
                    else:
                        self.status_label.setText("Status: Ready")
                        self._style_status("ready")

        win = self.window()
        if hasattr(win, "tabs"):
            for i in range(win.tabs.count()):
                w = win.tabs.widget(i)
                if hasattr(w, "check_for_set_up"):
                    try:
                        w.check_for_set_up()
                    except Exception:
                        pass

    def choose_folder(self, folder_type: str):
        settings = self.rl_manager.settings
        if folder_type == "rocket_league":
            path, _ = QFileDialog.getOpenFileName(self, "Select Rocket League exe", "", "Executables (*.exe)")
            if path:
                self.rl_manager.rocket_league_path = path
                settings.setValue("rocket_league_path", path)
        else:
            folder = QFileDialog.getExistingDirectory(self, f"Choose {folder_type} folder")
            if folder:
                if folder_type == "save":
                    self.rl_manager.save_path = folder
                    err = self.rl_manager.check_folders_identical()
                    err2 = self.rl_manager.check_path_contains_save_files()
                    if err:
                        self.rl_manager.save_path = ""
                        show_error(self, err)
                    elif err2:
                        self.rl_manager.save_path = ""
                        show_error(self, err2)
                    settings.setValue("save_path", self.rl_manager.save_path)
                elif folder_type == "backup":
                    self.rl_manager.backup_path = folder
                    err = self.rl_manager.check_folders_identical()
                    if err:
                        self.rl_manager.backup_path = ""
                        show_error(self, err)
                    self.rl_manager.settings.setValue("backup_path", self.rl_manager.backup_path)
        self.update_all_labels_and_status()

    def unset_folder(self, folder_type: str):
        settings = self.rl_manager.settings
        if folder_type == "rocket_league":
            self.rl_manager.rocket_league_path = ""
            settings.setValue("rocket_league_path", "")
        elif folder_type == "save":
            self.rl_manager.save_path = ""
            settings.setValue("save_path", "")
        elif folder_type == "backup":
            self.rl_manager.backup_path = ""
            settings.setValue("backup_path", "")
        self.update_all_labels_and_status()

    def store_latest_saves(self):
        err = self.rl_manager.check_folder_paths_set()
        if err:
            show_error(self, err)
            return
        copied = self.rl_manager.duplicate_save()
        if copied:
            names = [os.path.basename(p) for p in copied]
            QMessageBox.information(self, "Info", "Saved backups:\n" + "\n".join(names))
        else:
            QMessageBox.information(self, "Info", "No saves found to back up.")

# --- Skip Intro Tab ---
class SkipIntroTab(RequiresSetupTab):
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
            "Skip Intro",
            "Start Rocket League with the new account. The tool will wait for the game to create new .save files and then replace them with your backed up saves."
        )
        main.addWidget(instr_card)

        self.btn_skip = QPushButton("Skip Intro")
        self.btn_skip.setFixedWidth(200)
        main.addWidget(self.btn_skip, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("Status: -")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #d0d0d8;")
        main.addWidget(self.status_label)

        outer = QVBoxLayout(self)
        outer.addWidget(scroll)

        self.btn_skip.clicked.connect(self.run_skip_intro)
        self.check_for_set_up()

    def check_for_set_up(self):
        ready = bool(self.rl_manager.save_path and self.rl_manager.backup_path and self.rl_manager.rocket_league_path)
        self.btn_skip.setEnabled(ready)
        if not ready:
            self.status_label.setText("Status: Please finish setup first.")
            self.status_label.setStyleSheet("color: #f0b36b;")
        else:
            self.status_label.setText("Status: Ready")
            self.status_label.setStyleSheet("color: #86d07f;")

    def log_status(self, text: str, color: str = "#d0d0d8"):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color};")
        QApplication.processEvents()

    def run_skip_intro(self):
        err = self.rl_manager.check_folder_paths_set()
        if err:
            show_error(self, err)
            return
        self.log_status("Starting Rocket League and waiting for new save files...", "#f0c36b")
        try:
            ok = self.rl_manager.generate_new_save_files(timeout=180)
            if ok:
                self.log_status("Skip Intro completed — backup replaced.", "#86d07f")
                QMessageBox.information(self, "Done", "Skip Intro completed.")
            else:
                self.log_status("Skip Intro did not complete.", "#d97777")
                QMessageBox.information(self, "Info", "Skip Intro did not complete.")
        except Exception as e:
            self.log_status("Error occurred.", "#d97777")
            show_error(self, str(e))

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
            "Migrate Settings",
            "Copy settings from your primary account to the new account save. Ensure both save files are present and that you have backed up your originals."
        )
        main.addWidget(instr_card)

        self.btn_migrate = QPushButton("Migrate Settings")
        self.btn_migrate.setFixedWidth(220)
        main.addWidget(self.btn_migrate, alignment=Qt.AlignmentFlag.AlignCenter)

        self.status_label = QLabel("Status: -")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #d0d0d8;")
        main.addWidget(self.status_label)

        outer = QVBoxLayout(self)
        outer.addWidget(scroll)

        self.btn_migrate.clicked.connect(self.run_migration)
        self.check_for_set_up()

    def check_for_set_up(self):
        ready = bool(self.rl_manager.save_path and self.rl_manager.backup_path and self.rl_manager.rocket_league_path)
        self.btn_migrate.setEnabled(ready)
        if not ready:
            self.status_label.setText("Status: Please finish setup first.")
            self.status_label.setStyleSheet("color: #f0b36b;")
        else:
            self.status_label.setText("Status: Ready")
            self.status_label.setStyleSheet("color: #86d07f;")

    def log_status(self, text: str, color: str = "#d0d0d8"):
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color};")
        QApplication.processEvents()

    def run_migration(self):
        err = self.rl_manager.check_folder_paths_set()
        if err:
            show_error(self, err)
            return
        self.log_status("Restoring backup files...", "#f0c36b")
        latest = self.rl_manager.latest_saves()
        if latest:
            self.rl_manager.restore_backup(os.path.basename(latest[0]))
            self.log_status("Settings migrated successfully!", "#86d07f")
            QMessageBox.information(self, "Done", "Settings migrated successfully.")
        else:
            self.log_status("No saves found to migrate.", "#d97777")
            QMessageBox.information(self, "Info", "No saves found to migrate.")
