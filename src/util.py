import time
import psutil
import subprocess
import os
import glob
import re
import shutil
from PySide6.QtCore import QSettings
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class RLManager:
    def __init__(self):
        self.settings = QSettings("RLAccountMigrator", "Config")
        
        self.save_path_epic = self.settings.value("save_path_epic", "")
        self.rocket_league_path_epic = self.settings.value("rocket_league_path_epic", "")

        self.save_path_steam = self.settings.value("save_path_steam", "")  
        self.rocket_league_path_steam = self.settings.value("rocket_league_path_steam", "")

        self.backup_path = self.settings.value("backup_path", "")
        self.cretate_save_backup_folder()

    def cretate_save_backup_folder(self):
        self.backup_path = os.path.join(os.path.expanduser("~"), ".RLAccountMigrator", "saves_backup")        
        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path)
        self.settings.setValue("backup_path", self.backup_path)
    
    def get_rocket_league_locations(self):
        results = defaultdict(list)

        found_in_standard = self._check_standard_locations(results)

        if not found_in_standard:
            print("Standard locations not found. Starting a full drive scan...")
            self._full_drive_scan(results)

        return dict(results)

    def _check_standard_locations(self, results):
        if sys.platform == "win32":
            steam_apps_path = Path("C:") / "Program Files (x86)" / "Steam" / "steamapps" / "common" / "rocketleague"
            epic_apps_path = Path("C:") / "Program Files" / "Epic Games" / "RocketLeague"
            documents_path = Path.home() / "Documents" / "My Games" / "Rocket League" / "TAGame"

            steam_exe = steam_apps_path / "Binaries" / "Win64" / "RocketLeague.exe"
            if steam_exe.exists():
                results["Steam_exe"].append(str(steam_exe))
                self.settings.setValue("rocket_league_path_steam", str(steam_exe))
                self.rocket_league_path_steam = str(steam_exe)

            epic_exe = epic_apps_path / "Binaries" / "Win64" / "RocketLeague.exe"
            if epic_exe.exists():
                results["Epic_exe"].append(str(epic_exe))
                self.settings.setValue("rocket_league_path_epic", str(epic_exe))
                self.rocket_league_path_epic = str(epic_exe)

            epic_save_folder = documents_path / "SaveDataEpic" / "DBE_Production"
            if epic_save_folder.exists():
                results["Epic_folder"].append(str(epic_save_folder))
                self.settings.setValue("save_path_epic", str(epic_save_folder))
                self.save_path_epic = str(epic_save_folder)

            steam_save_folder = documents_path / "SaveData" / "DBE_Production"
            if steam_save_folder.exists():
                results["Steam_folder"].append(str(steam_save_folder))
                self.settings.setValue("save_path_steam", str(steam_save_folder))
                self.save_path_steam = str(steam_save_folder)

        elif sys.platform.startswith("linux"):
            pass

        elif sys.platform == "darwin": # macOS 
            pass

        all_found = len(results["Epic_exe"]) > 0 and len(results["Steam_exe"]) > 0 and \
                    len(results["Epic_folder"]) > 0 and len(results["Steam_folder"]) > 0

        return all_found

    def _full_drive_scan(self, results):
        for p in psutil.disk_partitions():
            root_drive = Path(p.mountpoint)
            if not root_drive.exists():
                continue

            try:
                for path in root_drive.rglob("DBE_Production"):
                    path_parts_lower = [part.lower() for part in path.parts]
                    if "onedrive" in path_parts_lower:
                        continue
                    if "savedataepic" in path_parts_lower:
                        results["Epic_folder"].append(str(path))
                        self.settings.setValue("save_path_epic", str(path))
                        self.save_path_epic = str(path)
                    elif "savedata" in path_parts_lower:
                        results["Steam_folder"].append(str(path))
                        self.settings.setValue("save_path_steam", str(path))
                        self.save_path_steam = str(path)

                for path in root_drive.rglob("RocketLeague.exe"):
                    path_parts_lower = [part.lower() for part in path.parts]
                    if any(l in path_parts_lower for l in ["steamapps", "steam"]):
                        results["Steam_exe"].append(str(path))
                        self.settings.setValue("rocket_league_path_steam", str(path))
                        self.rocket_league_path_steam = str(path)
                    elif any(l in path_parts_lower for l in ["epic games", "epicgames"]):
                        results["Epic_exe"].append(str(path))
                        self.settings.setValue("rocket_league_path_epic", str(path))
                        self.rocket_league_path_epic = str(path)

            except (PermissionError, OSError) as e:
                print(f"Skipping {root_drive} due to error: {e}")
                continue
            
    def latest_saves(self, platform: str = "steam" or "epic"):
    
        saves = []
        if platform == "steam":
            saves = glob.glob(os.path.join(self.save_path_steam, "*.save"))
        elif platform == "epic":
            saves = glob.glob(os.path.join(self.save_path_epic, "*.save"))
        if not saves:
            return []
        
        today = datetime.today().date()

        saves = [f for f in saves if datetime.fromtimestamp(os.path.getmtime(f)).date() == today]
        if not saves:
            return []
        


        newest_file = max(saves, key=os.path.getmtime)

        match = re.match(r"([a-f0-9]+)(?:_\d+)?\.save$", os.path.basename(newest_file))
        if not match:
            return []
        newest_base = match.group(1)

        base_files = [f for f in saves if re.match(rf"{newest_base}(?:_\d+)?\.save$", os.path.basename(f))]

        base_files.sort(key=os.path.getmtime, reverse=True)

        return base_files

    def duplicate_save(self, platform: str = "steam" or "epic"):
        latest_list = self.latest_saves(platform)
        if latest_list:
            existing_files = glob.glob(os.path.join(self.backup_path, "*.save"))
            if len(existing_files) == 0:
                for latest in latest_list:
                    copy_target = os.path.join(self.backup_path, os.path.basename(latest))
                    shutil.copy2(latest, copy_target)
                return latest_list
            else:
                error = "Backup folder is not empty! Please clear it before creating a new backup."
                return error 
        return None
    
    def wait_for_new_latest_save(self, timeout: int, platform: str = "steam" or "epic"):
        save_path = ""
        if platform == "steam":
            save_path = self.save_path_steam
        elif platform == "epic":
            save_path = self.save_path_epic

        existing_files = glob.glob(os.path.join(save_path, "*.save"))
        existing_bases = set()
        for f in existing_files:
            match = re.match(r"([a-f0-9]+)(?:_\d+)?\.save$", os.path.basename(f))
            if match:
                existing_bases.add(match.group(1))

        start_time = time.time()
        today = datetime.today().date()

        while time.time() - start_time < timeout:
            current_files = glob.glob(os.path.join(save_path, "*.save"))
            new_bases = set()
            for f in current_files:
                match = re.match(r"([a-f0-9]+)(?:_\d+)?\.save$", os.path.basename(f))
                if match:
                    base = match.group(1)
                    if base not in existing_bases:
                        new_bases.add(base)

            if new_bases:
                newest_file = max(current_files, key=os.path.getmtime)
                newest_base = re.match(r"([a-f0-9]+)(?:_\d+)?\.save$", os.path.basename(newest_file)).group(1)

                file_date = datetime.fromtimestamp(os.path.getmtime(newest_file)).date()
                if file_date != today:
                    time.sleep(2)
                    continue

                if newest_base in new_bases:
                    base_files = [
                        f for f in current_files
                        if re.match(rf"{newest_base}(?:_\d+)?\.save$", os.path.basename(f))
                    ]
                    base_files.sort(key=os.path.getmtime, reverse=True)
                    return base_files

            time.sleep(2)

        return self.latest_saves(platform=platform)

    def get_base_name(self, filename):
        match = re.match(r"([a-f0-9]+)(?:_\d+)?\.save$", os.path.basename(filename))
        return match.group(1) if match else None

    def replace_save_files_with_backup(self, base_name, platform: str = "steam" or "epic"):
        save_path = ""
        if platform == "steam":
            save_path = self.save_path_steam
        elif platform == "epic":
            save_path = self.save_path_epic
        
        for f in os.listdir(save_path):
            if re.match(rf"{base_name}(?:_\d+)?\.save$", f):
                os.remove(os.path.join(save_path, f))

        for f in os.listdir(self.backup_path):
            shutil.copy2(os.path.join(self.backup_path, f), os.path.join(save_path, base_name + f[len(base_name):]))

    def backup_save_files_for_new_ones(self, base_name, platform: str = "steam" or "epic"):
        save_path = ""
        if platform == "steam":
            save_path = self.save_path_steam
        elif platform == "epic":
            save_path = self.save_path_epic

        for f in os.listdir(self.backup_path):
            os.remove(os.path.join(self.backup_path, f))
        for f in os.listdir(save_path):
            if re.match(rf"{base_name}(?:_\d+)?\.save$", f):
                shutil.copy2(os.path.join(save_path, base_name + f[len(base_name):]), os.path.join(self.backup_path, f))

    def generate_new_save_files(self, mode: str = "get_backup" or "replace_existing", platform: str = "steam" or "epic"):
        rocket_league_path = ""
        if platform == "steam":
            rocket_league_path = self.rocket_league_path_steam
        elif platform == "epic":
            rocket_league_path = self.rocket_league_path_epic
        
        
        if not (rocket_league_path and os.path.exists(rocket_league_path)):
            return False

        subprocess.Popen([rocket_league_path])

        try:
            latest_files = self.wait_for_new_latest_save(timeout=60, platform=platform)
            if not latest_files:
                return False

            base_name = self.get_base_name(latest_files[0])
            if not base_name:
                return False

            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and 'RocketLeague' in proc.info['name']:
                    try:
                        proc.terminate()
                        proc.wait(timeout=10)
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        proc.kill()

            if mode == "replace_existing":
                self.replace_save_files_with_backup(base_name, platform=platform)
            elif mode == "get_backup":
                self.backup_save_files_for_new_ones(base_name, platform=platform)
            return True

        except TimeoutError:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and 'RocketLeague' in proc.info['name']:
                    try:
                        proc.terminate()
                        proc.wait(timeout=10)
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        proc.kill()
            raise

    # --- Check-Funktion ---
    def check_folder_paths_set(self, platform: str = "steam" or "epic"):
        save_path = ""
        if platform == "steam":
            save_path = self.save_path_steam
        elif platform == "epic":
            save_path = self.save_path_epic
       
        if not save_path or not self.backup_path:
            return "Please select both a save and backup folders!"
    
    def check_backup_folder_empty(self):
        file_count = []
        for f in os.listdir(self.backup_path):
            file_count.append(f)
        if len(file_count) == 0:
            return "No saves backed up to copy"

    def check_folders_identical(self, platform: str = "steam" or "epic"):
        save_path = ""
        if platform == "steam":
            save_path = self.save_path_steam
        elif platform == "epic":
            save_path = self.save_path_epic
        
        if os.path.abspath(save_path) == os.path.abspath(self.backup_path):
            return "Save folder and backup folder cant be the same folder!"
        
    def check_path_contains_save_files(self, platform: str = "steam" or "epic"):
        save_path = ""
        if platform == "steam":
            save_path = self.save_path_steam
        elif platform == "epic":
            save_path = self.save_path_epic
        
        try:
            save_files = [f for f in os.listdir(save_path) if f.endswith(".save")]
            if not save_files:
                return "No .save file found in the save folder!"
            return None
        except FileNotFoundError:
            return None
        
    def check_all_paths_set(self):
        if self.backup_path and self.save_path_epic and self.save_path_steam and self.rocket_league_path_epic and self.rocket_league_path_steam:
            return {"text":"Config status: all set", "color":"#86d07f"}
        elif self.backup_path and self.save_path_epic and self.rocket_league_path_epic and not self.rocket_league_path_steam or not self.save_path_steam:
            return {"text":"Config status: steam needs configuration", "color":"#b77b00"}
        elif self.backup_path and self.save_path_steam and self.rocket_league_path_steam and not self.rocket_league_path_epic or not self.save_path_epic:
            return {"text":"Config status: epic needs configuration", "color":"#b77b00"}
        return {"text":"Config status: epic and steam need configuration", "color":"#7a7aa8"}