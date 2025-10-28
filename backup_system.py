"""
Complete Disaster Recovery Backup System
Automated backup and restore to Azure Blob Storage
"""
import os
import json
import logging
from datetime import datetime
from azure.storage.blob import BlobServiceClient
import hashlib
import time
import zipfile
import tempfile

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackupSystem:
    """Handles backup and restore operations"""
    
    def __init__(self):
        """Initialize Azure Storage connection"""
        self.connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.container_name = os.getenv('AZURE_CONTAINER_NAME', 'backups')
        
        if not self.connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING not set")
        
        try:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            self.container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
            # Test connection
            self.container_client.get_container_properties()
            logger.info("Azure Storage connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Azure Storage: {str(e)}")
            raise
    
    def backup_file(self, file_path, backup_name=None):
        """
        Backup a single file to Azure Storage
        
        Args:
            file_path: Path to file to backup
            backup_name: Custom name for backup (optional)
            
        Returns:
            dict: Backup metadata including time taken
        """
        start_time = time.time()
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Generate backup name with timestamp
        if not backup_name:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.basename(file_path)
            backup_name = f"backup_{timestamp}_{filename}"
        
        # Get file size
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)
        
        logger.info(f"📦 Backing up: {file_path} ({file_size_mb:.2f} MB)")
        
        # Calculate file hash for integrity verification
        file_hash = self._calculate_hash(file_path)
        
        # Upload to Azure
        blob_client = self.container_client.get_blob_client(backup_name)
        
        with open(file_path, 'rb') as data:
            blob_client.upload_blob(data, overwrite=True)
        
        upload_time = time.time() - start_time
        
        # Create metadata
        metadata = {
            'backup_name': backup_name,
            'original_file': file_path,
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size_mb, 2),
            'file_hash': file_hash,
            'upload_time_seconds': round(upload_time, 2),
            'timestamp': datetime.now().isoformat(),
            'status': 'success',
            'backup_type': 'file'
        }
        
        # Save metadata
        self._save_metadata(backup_name, metadata)
        
        logger.info(f"✅ Backup completed in {upload_time:.2f} seconds")
        
        return metadata
    
    def backup_directory(self, directory_path, backup_prefix=None, create_zip=True):
        """
        Backup entire directory to Azure Storage
        
        Args:
            directory_path: Path to directory to backup
            backup_prefix: Prefix for backup (optional)
            create_zip: Create a single zip file (True) or individual files (False)
            
        Returns:
            dict: Backup summary with timing information
        """
        start_time = time.time()
        
        if not os.path.isdir(directory_path):
            raise NotADirectoryError(f"Not a directory: {directory_path}")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if not backup_prefix:
            dir_name = os.path.basename(os.path.normpath(directory_path))
            backup_prefix = f"backup_{timestamp}_{dir_name}"
        
        logger.info(f"📂 Starting directory backup: {directory_path}")
        
        if create_zip:
            # Create zip file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
                zip_path = tmp.name
            
            logger.info(f"📦 Creating zip archive...")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(directory_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, directory_path)
                        zipf.write(file_path, arcname)
            
            # Backup the zip file
            zip_backup_name = f"{backup_prefix}.zip"
            metadata = self.backup_file(zip_path, zip_backup_name)
            
            # Clean up temp file
            os.unlink(zip_path)
            
            total_time = time.time() - start_time
            
            summary = {
                'backup_name': zip_backup_name,
                'backup_type': 'directory_zip',
                'directory': directory_path,
                'file_size_mb': metadata['file_size_mb'],
                'total_time_seconds': round(total_time, 2),
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        else:
            # Backup individual files
            backed_up_files = []
            total_size = 0
            
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory_path)
                    backup_name = f"{backup_prefix}/{relative_path}"
                    
                    try:
                        file_metadata = self.backup_file(file_path, backup_name)
                        backed_up_files.append(file_metadata)
                        total_size += file_metadata['file_size_bytes']
                    except Exception as e:
                        logger.error(f"❌ Failed to backup {file_path}: {str(e)}")
            
            total_time = time.time() - start_time
            
            summary = {
                'backup_prefix': backup_prefix,
                'backup_type': 'directory_individual',
                'directory': directory_path,
                'files_backed_up': len(backed_up_files),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'total_time_seconds': round(total_time, 2),
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'files': backed_up_files
            }
        
        logger.info(f"✅ Directory backup completed in {summary['total_time_seconds']} seconds")
        
        return summary
    
    def list_backups(self):
        """
        List all backups in Azure Storage
        
        Returns:
            list: List of backup information
        """
        backups = []
        
        try:
            for blob in self.container_client.list_blobs():
                # Skip metadata files
                if blob.name.endswith('.metadata.json'):
                    continue
                
                backup_info = {
                    'name': blob.name,
                    'size_bytes': blob.size,
                    'size_mb': round(blob.size / (1024 * 1024), 2),
                    'created': blob.creation_time.isoformat() if blob.creation_time else None,
                    'last_modified': blob.last_modified.isoformat() if blob.last_modified else None,
                    'url': f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob.name}"
                }
                backups.append(backup_info)
            
            logger.info(f"📋 Found {len(backups)} backups")
            return backups
        except Exception as e:
            logger.error(f"❌ Failed to list backups: {str(e)}")
            raise
    
    def restore_file(self, backup_name, restore_path):
        """
        Restore a file from Azure Storage
        
        Args:
            backup_name: Name of backup in Azure
            restore_path: Local path to restore to
            
        Returns:
            dict: Restore metadata with timing
        """
        start_time = time.time()
        
        logger.info(f"🔄 Restoring: {backup_name} -> {restore_path}")
        
        blob_client = self.container_client.get_blob_client(backup_name)
        
        # Create directory if needed
        os.makedirs(os.path.dirname(restore_path) or '.', exist_ok=True)
        
        # Download from Azure
        with open(restore_path, 'wb') as file:
            data = blob_client.download_blob()
            file.write(data.readall())
        
        restore_time = time.time() - start_time
        file_size = os.path.getsize(restore_path)
        
        metadata = {
            'backup_name': backup_name,
            'restored_to': restore_path,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'restore_time_seconds': round(restore_time, 2),
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
        
        logger.info(f"✅ Restore completed in {restore_time:.2f} seconds")
        
        return metadata
    
    def delete_backup(self, backup_name):
        """Delete a backup from Azure Storage"""
        try:
            blob_client = self.container_client.get_blob_client(backup_name)
            blob_client.delete_blob()
            
            # Also delete metadata if exists
            metadata_name = f"{backup_name}.metadata.json"
            try:
                metadata_blob = self.container_client.get_blob_client(metadata_name)
                metadata_blob.delete_blob()
            except:
                pass
            
            logger.info(f"🗑️  Deleted backup: {backup_name}")
            return {
                'status': 'deleted',
                'backup_name': backup_name,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Failed to delete {backup_name}: {str(e)}")
            raise
    
    def get_storage_stats(self):
        """Get storage usage statistics"""
        backups = self.list_backups()
        
        total_size = sum(b['size_bytes'] for b in backups)
        total_size_mb = total_size / (1024 * 1024)
        total_size_gb = total_size / (1024 * 1024 * 1024)
        
        return {
            'total_backups': len(backups),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size_mb, 2),
            'total_size_gb': round(total_size_gb, 2),
            'oldest_backup': min((b['created'] for b in backups if b['created']), default=None),
            'newest_backup': max((b['created'] for b in backups if b['created']), default=None),
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_hash(self, file_path):
        """Calculate SHA256 hash of file for integrity verification"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _save_metadata(self, backup_name, metadata):
        """Save backup metadata to Azure Storage"""
        try:
            metadata_name = f"{backup_name}.metadata.json"
            blob_client = self.container_client.get_blob_client(metadata_name)
            
            metadata_json = json.dumps(metadata, indent=2)
            blob_client.upload_blob(metadata_json, overwrite=True)
        except Exception as e:
            logger.warning(f"⚠️  Failed to save metadata: {str(e)}")
