"""Core Backup Module"""
import os
import zipfile
import datetime
import json
import logging
from pathlib import Path
from config import BACKUP_CONFIG, LOG_CONFIG

# Setup logging
logging.basicConfig(
    filename=LOG_CONFIG["log_file"],
    level=LOG_CONFIG["log_level"],
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BackupSystem:
    def __init__(self):
        self.config = BACKUP_CONFIG
        self.backup_dir = Path(self.config["backup_location"])
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def create_backup(self):
        """Create a backup of all configured source directories"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_name = f"backup_{timestamp}.zip"
            backup_path = self.backup_dir / backup_name
            
            logging.info(f"Starting backup: {backup_name}")
            print(f"📦 Creating backup: {backup_name}")
            
            total_files = 0
            total_size = 0
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for source_dir in self.config["source_dirs"]:
                    source_path = Path(source_dir)
                    if not source_path.exists():
                        logging.warning(f"Source directory not found: {source_dir}")
                        continue
                    
                    for root, dirs, files in os.walk(source_path):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to(source_path.parent)
                            zipf.write(file_path, arcname)
                            total_files += 1
                            total_size += file_path.stat().st_size
            
            # Create metadata
            metadata = {
                "backup_name": backup_name,
                "timestamp": timestamp,
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "source_dirs": self.config["source_dirs"],
            }
            
            # Save metadata
            metadata_path = self.backup_dir / f"{backup_name}.meta"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logging.info(f"Backup completed: {backup_name}")
            print(f"✅ Backup completed: {total_files} files, {metadata['total_size_mb']} MB")
            
            return True, backup_name, metadata
                
        except Exception as e:
            logging.error(f"Backup failed: {str(e)}")
            print(f"❌ Backup failed: {str(e)}")
            return False, None, None
    
    def list_backups(self):
        """List all available backups"""
        try:
            backups = []
            for backup_file in self.backup_dir.glob("backup_*.zip"):
                metadata_file = backup_file.with_suffix('.zip.meta')
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    backups.append(metadata)
            return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
        except Exception as e:
            logging.error(f"Failed to list backups: {str(e)}")
            return []
    
    def get_backup_stats(self):
        """Get statistics about backups"""
        backups = self.list_backups()
        total_size = sum(b.get("total_size_mb", 0) for b in backups)
        return {
            "total_backups": len(backups),
            "total_size_mb": round(total_size, 2),
            "latest_backup": backups[0]["timestamp"] if backups else "No backups yet",
        }

if __name__ == "__main__":
    print("🛡️ Automated Disaster Recovery Backup System")
    print("=" * 50)
    backup_system = BackupSystem()
    success, backup_name, metadata = backup_system.create_backup()
    if success:
        print(f"\n✅ Backup successful: {backup_name}")
