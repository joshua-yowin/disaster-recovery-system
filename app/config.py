"""Configuration Management"""
import os
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "sample_data"
BACKUP_DIR = BASE_DIR / "backups"
LOG_DIR = BASE_DIR / "logs"


# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


# Azure Configuration
AZURE_CONFIG = {
    "connection_string": os.getenv("AZURE_STORAGE_CONNECTION_STRING", ""),
    "container_name": os.getenv("AZURE_CONTAINER_NAME", "backups"),
    "storage_account": os.getenv("AZURE_STORAGE_ACCOUNT", ""),
}


# Backup Configuration
BACKUP_CONFIG = {
    "source_dirs": [str(DATA_DIR)],
    "backup_location": str(BACKUP_DIR),
    "retention_days": int(os.getenv("RETENTION_DAYS", "30")),
    "compression": "zip",
}


# Logging Configuration
LOG_CONFIG = {
    "log_file": str(LOG_DIR / "backup_system.log"),
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
}


# Dashboard Configuration - UPDATED PORT AND DEBUG
DASHBOARD_CONFIG = {
    "host": os.getenv("DASHBOARD_HOST", "0.0.0.0"),
    "port": int(os.getenv("DASHBOARD_PORT", "5001")),  # Changed from 5000 to 5001
    "debug": os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes"),  # Changed default to True
}
