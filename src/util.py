import time
import psutil
import subprocess
import os
import glob
import re
import shutil
from PySide6.QtCore import QSettings

class RLManager:
    def __init__(self):
        # QSettings beim Start laden
        self.settings = QSettings("Maizu", "RLAccountMigrator")
        
        self.save_path = self.settings.value("save_path", "") 
        self.backup_path = self.settings.value("backup_path", "")
        self.rocket_league_path = self.settings.value("rocket_league_path", "")

    def latest_saves(self):
    
        # Alle .save-Dateien sammeln
        saves = glob.glob(os.path.join(self.save_path, "*.save"))
        if not saves:
            return []

        # Neueste Datei nach Änderungszeit bestimmen
        newest_file = max(saves, key=os.path.getmtime)

        # Base-ID der neuesten Datei
        match = re.match(r"([a-f0-9]+)(?:_\d+)?\.save$", os.path.basename(newest_file))
        if not match:
            return []
        newest_base = match.group(1)

        # Alle Dateien mit derselben Base-ID
        base_files = [f for f in saves if re.match(rf"{newest_base}(?:_\d+)?\.save$", os.path.basename(f))]

        # Optional: nach Änderungszeit sortieren (neueste zuerst)
        base_files.sort(key=os.path.getmtime, reverse=True)

        return base_files

    def duplicate_save(self):
        latest_list = self.latest_saves()
        if latest_list:
            # Dupliziere die **neusten** Datei aus der Liste
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
    def wait_for_new_latest_save(self, timeout=30):
        # vorhandene Base-IDs merken
        existing_files = glob.glob(os.path.join(self.save_path, "*.save"))
        existing_bases = set()
        for f in existing_files:
            match = re.match(r"([a-f0-9]+)(?:_\d+)?\.save$", os.path.basename(f))
            if match:
                existing_bases.add(match.group(1))

        start_time = time.time()
        while time.time() - start_time < timeout:
            current_files = glob.glob(os.path.join(self.save_path, "*.save"))
            # finde neue Base-IDs
            new_bases = set()
            for f in current_files:
                match = re.match(r"([a-f0-9]+)(?:_\d+)?\.save$", os.path.basename(f))
                if match:
                    base = match.group(1)
                    if base not in existing_bases:
                        new_bases.add(base)

            if new_bases:
                # Nimm die Base-ID der neuesten Datei
                newest_file = max(current_files, key=os.path.getmtime)
                newest_base = re.match(r"([a-f0-9]+)(?:_\d+)?\.save$", os.path.basename(newest_file)).group(1)
                if newest_base in new_bases:
                    # alle Dateien dieser Base-ID zurückgeben
                    base_files = [f for f in current_files if re.match(rf"{newest_base}(?:_\d+)?\.save$", os.path.basename(f))]
                    base_files.sort(key=os.path.getmtime, reverse=True)
                    return base_files

            time.sleep(2)

        return self.latest_saves()

    def get_base_name(self, filename):
        match = re.match(r"([a-f0-9]+)(?:_\d+)?\.save$", os.path.basename(filename))
        return match.group(1) if match else None

    def replace_save_files_with_backup(self, base_name):
        # Alte Dateien löschen
        for f in os.listdir(self.save_path):
            if re.match(rf"{base_name}(?:_\d+)?\.save$", f):
                os.remove(os.path.join(self.save_path, f))

        # Backup-Dateien kopieren
        for f in os.listdir(self.backup_path):
            shutil.copy2(os.path.join(self.backup_path, f), os.path.join(self.save_path, base_name + f[len(base_name):]))

    def generate_new_save_files(self):
        if not (self.rocket_league_path and os.path.exists(self.rocket_league_path)):
            return False

        # Rocket League starten
        subprocess.Popen([self.rocket_league_path])

        try:
            # Warten bis neue Save-Dateien erstellt werden
            latest_files = self.wait_for_new_latest_save(timeout=60)
            if not latest_files:
                return False

            # Base-Name der neuesten Datei
            base_name = self.get_base_name(latest_files[0])
            if not base_name:
                return False

            # Rocket League Prozess beenden
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and 'RocketLeague' in proc.info['name']:
                    try:
                        proc.terminate()
                        proc.wait(timeout=10)
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        proc.kill()

            # Jetzt die alten Dateien der Base-ID löschen und Backup kopieren
            self.replace_save_files_with_backup(base_name)

            return True

        except TimeoutError:
            # Rocket League Prozesse ebenfalls beenden, falls Timeout erreicht
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and 'RocketLeague' in proc.info['name']:
                    try:
                        proc.terminate()
                        proc.wait(timeout=10)
                    except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                        proc.kill()
            raise


    def create_new_account_save_files_from_backup(self, old_name, new_name):
        old_file = os.path.join(self.save_path, old_name)
        new_file = os.path.join(self.save_path, new_name)
        if os.path.exists(old_file):
            os.rename(old_file, new_file)
            return True
        return False

    def restore_backup(self, new_name):
        for f in os.listdir(self.backup_path):
            if f.endswith(".save"):
                src = os.path.join(self.backup_path, f)
                dst = os.path.join(self.save_path, new_name)
                shutil.copy2(src, dst)


    # --- Check-Funktion ---
    def check_folder_paths_set(self):
        if not self.save_path or not self.backup_path:
            return "Please select both a save and backup folders!"
        
    def check_folders_identical(self):
        if os.path.abspath(self.save_path) == os.path.abspath(self.backup_path):
            return "Save folder and backup folder cant be the same folder!"
        
    def check_path_contains_save_files(self):
        # mindestens eine .save Datei im Save-Ordner
        try:
            save_files = [f for f in os.listdir(self.save_path) if f.endswith(".save")]
            if not save_files:
                return "No .save file found in the save folder!"
            return None
        except FileNotFoundError:
            return None