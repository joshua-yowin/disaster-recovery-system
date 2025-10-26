"""Restore Module"""
import zipfile
import json
import logging
from pathlib import Path
from config import BACKUP_CONFIG, LOG_CONFIG

logging.basicConfig(
    filename=LOG_CONFIG["log_file"],
    level=LOG_CONFIG["log_level"],
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RestoreSystem:
    def __init__(self):
        self.config = BACKUP_CONFIG
        self.backup_dir = Path(self.config["backup_location"])
        
    def restore_backup(self, backup_name, restore_location=None):
        """Restore a specific backup"""
        try:
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                logging.error(f"Backup not found: {backup_name}")
                return False
            
            if restore_location is None:
                restore_location = Path(self.config["backup_location"]).parent / "restored"
            else:
                restore_location = Path(restore_location)
            
            restore_location.mkdir(parents=True, exist_ok=True)
            
            logging.info(f"Starting restore: {backup_name} to {restore_location}")
            print(f"♻️  Restoring backup: {backup_name}")
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(restore_location)
                total_files = len(zipf.namelist())
            
            logging.info(f"Restore completed: {total_files} files restored")
            print(f"✅ Restore completed: {total_files} files")
            return True
            
        except Exception as e:
            logging.error(f"Restore failed: {str(e)}")
            print(f"❌ Restore failed: {str(e)}")
            return False
