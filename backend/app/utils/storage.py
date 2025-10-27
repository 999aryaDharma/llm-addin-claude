"""
Storage utilities for file management
"""
import asyncio

import hashlib
import shutil
from pathlib import Path
from typing import Optional, BinaryIO
from datetime import datetime
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class StorageManager:
    """Manage file uploads and storage"""
    
    def __init__(self):
        self.upload_path = Path(settings.UPLOAD_PATH)
        self.upload_path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def generate_file_hash(file_content: bytes) -> str:
        """Generate SHA256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()
    
    async def save_file(
        self,
        file_content: bytes,
        filename: str,
        subfolder: Optional[str] = None
    ) -> Path:
        """Save file to upload directory"""
        try:
            # Create subfolder if specified
            if subfolder:
                save_path = self.upload_path / subfolder
                save_path.mkdir(parents=True, exist_ok=True)
            else:
                save_path = self.upload_path
            
            # Generate unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = self.generate_file_hash(file_content)[:8]
            name, ext = Path(filename).stem, Path(filename).suffix
            unique_filename = f"{name}_{timestamp}_{file_hash}{ext}"
            
            file_path = save_path / unique_filename

            # Save file asynchronously
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: file_path.write_bytes(file_content)
            )

            logger.info(f"File saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise
    
    async def read_file(self, file_path: Path) -> bytes:
        """Read file content asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(
                None,
                lambda: file_path.read_bytes()
            )
            return content
        except Exception as e:
            logger.error(f"Error reading file: {str(e)}")
            raise
    
    async def delete_file(self, file_path: Path) -> bool:
        """Delete a file"""
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise
    
    def get_file_info(self, file_path: Path) -> dict:
        """Get file metadata"""
        if not file_path.exists():
            return {}
        
        stat = file_path.stat()
        return {
            "filename": file_path.name,
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": file_path.suffix
        }
    
    def list_files(self, subfolder: Optional[str] = None) -> list:
        """List all files in upload directory"""
        if subfolder:
            search_path = self.upload_path / subfolder
        else:
            search_path = self.upload_path
        
        if not search_path.exists():
            return []
        
        files = []
        for file_path in search_path.iterdir():
            if file_path.is_file():
                files.append(self.get_file_info(file_path))
        
        return files
    
    def cleanup_old_files(self, days: int = 7):
        """Delete files older than specified days"""
        try:
            current_time = datetime.now().timestamp()
            cutoff_time = current_time - (days * 86400)  # days to seconds
            
            deleted_count = 0
            for file_path in self.upload_path.rglob('*'):
                if file_path.is_file():
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old files")
            return deleted_count
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            raise


# Global instance
storage_manager = StorageManager()