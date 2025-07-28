"""File storage service for document management."""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
import hashlib
import mimetypes

from ...config.settings import get_settings
from ...utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class FileStorageService:
    """
    File storage service for managing document files.
    
    Handles file storage, retrieval, and management with support
    for local storage and cloud storage backends.
    """
    
    def __init__(self):
        """Initialize file storage service."""
        self.storage_root = Path(settings.FILE_STORAGE_PATH)
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.documents_dir = self.storage_root / "documents"
        self.temp_dir = self.storage_root / "temp"
        self.thumbnails_dir = self.storage_root / "thumbnails"
        
        for directory in [self.documents_dir, self.temp_dir, self.thumbnails_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    async def store_file(
        self,
        file_path: str,
        plaintiff_id: Optional[str] = None,
        document_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store a file in the storage system.
        
        Args:
            file_path: Path to the source file.
            plaintiff_id: Optional plaintiff ID for organization.
            document_type: Optional document type for organization.
            metadata: Optional file metadata.
            
        Returns:
            dict: Storage result with file URL and metadata.
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Source file not found: {file_path}")
            
            source_path = Path(file_path)
            
            # Generate file hash for deduplication
            file_hash = self._calculate_file_hash(file_path)
            
            # Determine storage path
            storage_path = self._get_storage_path(
                source_path.name, 
                plaintiff_id, 
                document_type, 
                file_hash
            )
            
            # Ensure directory exists
            storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file to storage
            shutil.copy2(file_path, storage_path)
            
            # Get file metadata
            file_metadata = self._get_file_metadata(storage_path)
            if metadata:
                file_metadata.update(metadata)
            
            # Generate file URL
            file_url = self._generate_file_url(storage_path)
            
            logger.info(
                "File stored successfully",
                source_path=str(source_path),
                storage_path=str(storage_path),
                file_hash=file_hash,
            )
            
            return {
                "success": True,
                "file_url": file_url,
                "storage_path": str(storage_path),
                "file_hash": file_hash,
                "metadata": file_metadata,
            }
            
        except Exception as e:
            logger.error(f"Failed to store file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def get_file_path(self, file_url: str) -> str:
        """
        Get local file path from file URL.
        
        Args:
            file_url: File URL or path.
            
        Returns:
            str: Local file path.
        """
        if file_url.startswith('http'):
            # Parse URL to get path
            parsed = urlparse(file_url)
            relative_path = parsed.path.lstrip('/')
            return str(self.storage_root / relative_path)
        else:
            # Assume it's already a file path
            return file_url
    
    async def get_file_info(self, file_url: str) -> Dict[str, Any]:
        """
        Get file information and metadata.
        
        Args:
            file_url: File URL.
            
        Returns:
            dict: File information.
        """
        try:
            file_path = await self.get_file_path(file_url)
            
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": "File not found",
                }
            
            metadata = self._get_file_metadata(Path(file_path))
            
            return {
                "success": True,
                "file_path": file_path,
                "metadata": metadata,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    async def delete_file(self, file_url: str) -> Dict[str, Any]:
        """
        Delete a file from storage.
        
        Args:
            file_url: File URL to delete.
            
        Returns:
            dict: Deletion result.
        """
        try:
            file_path = await self.get_file_path(file_url)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                
                # Also remove thumbnail if exists
                thumbnail_path = self._get_thumbnail_path(Path(file_path))
                if thumbnail_path.exists():
                    os.remove(thumbnail_path)
                
                logger.info(f"File deleted: {file_path}")
                
                return {
                    "success": True,
                    "deleted_path": file_path,
                }
            else:
                return {
                    "success": False,
                    "error": "File not found",
                }
                
        except Exception as e:
            logger.error(f"Failed to delete file {file_url}: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def list_files(
        self,
        plaintiff_id: Optional[str] = None,
        document_type: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        List files in storage.
        
        Args:
            plaintiff_id: Filter by plaintiff ID.
            document_type: Filter by document type.
            limit: Maximum number of files to return.
            
        Returns:
            dict: List of files with metadata.
        """
        try:
            files = []
            search_dir = self.documents_dir
            
            # Apply filters to search directory
            if plaintiff_id:
                search_dir = search_dir / plaintiff_id
                if not search_dir.exists():
                    return {"success": True, "files": [], "total": 0}
            
            if document_type:
                search_dir = search_dir / document_type
                if not search_dir.exists():
                    return {"success": True, "files": [], "total": 0}
            
            # Walk through directory
            for file_path in search_dir.rglob("*"):
                if file_path.is_file() and len(files) < limit:
                    file_info = {
                        "file_url": self._generate_file_url(file_path),
                        "file_name": file_path.name,
                        "file_path": str(file_path),
                        "metadata": self._get_file_metadata(file_path),
                    }
                    files.append(file_info)
            
            return {
                "success": True,
                "files": files,
                "total": len(files),
            }
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def create_thumbnail(
        self,
        file_url: str,
        size: tuple = (200, 200)
    ) -> Dict[str, Any]:
        """
        Create thumbnail for image files.
        
        Args:
            file_url: Source file URL.
            size: Thumbnail size (width, height).
            
        Returns:
            dict: Thumbnail creation result.
        """
        try:
            file_path = Path(await self.get_file_path(file_url))
            
            if not file_path.exists():
                return {
                    "success": False,
                    "error": "Source file not found",
                }
            
            # Check if file is an image
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type or not mime_type.startswith('image/'):
                return {
                    "success": False,
                    "error": "File is not an image",
                }
            
            # Try to create thumbnail using PIL
            try:
                from PIL import Image
                
                thumbnail_path = self._get_thumbnail_path(file_path)
                thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
                
                with Image.open(file_path) as img:
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                    img.save(thumbnail_path, "JPEG", quality=85)
                
                thumbnail_url = self._generate_file_url(thumbnail_path)
                
                return {
                    "success": True,
                    "thumbnail_url": thumbnail_url,
                    "thumbnail_path": str(thumbnail_path),
                }
                
            except ImportError:
                return {
                    "success": False,
                    "error": "PIL not available for thumbnail creation",
                }
                
        except Exception as e:
            logger.error(f"Failed to create thumbnail for {file_url}: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file."""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def _get_storage_path(
        self,
        filename: str,
        plaintiff_id: Optional[str],
        document_type: Optional[str],
        file_hash: str
    ) -> Path:
        """Generate storage path for file."""
        # Use hash prefix for deduplication
        hash_prefix = file_hash[:2]
        
        # Build path components
        path_components = [self.documents_dir]
        
        if plaintiff_id:
            path_components.append(plaintiff_id)
        
        if document_type:
            path_components.append(document_type)
        
        path_components.extend([hash_prefix, f"{file_hash}_{filename}"])
        
        return Path(*path_components)
    
    def _get_thumbnail_path(self, file_path: Path) -> Path:
        """Generate thumbnail path for file."""
        relative_path = file_path.relative_to(self.storage_root)
        thumbnail_name = f"{file_path.stem}_thumb.jpg"
        return self.thumbnails_dir / relative_path.parent / thumbnail_name
    
    def _generate_file_url(self, file_path: Path) -> str:
        """Generate URL for file."""
        relative_path = file_path.relative_to(self.storage_root)
        return f"/files/{relative_path}"
    
    def _get_file_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Get file metadata."""
        stat = file_path.stat()
        mime_type, encoding = mimetypes.guess_type(str(file_path))
        
        return {
            "file_name": file_path.name,
            "file_size": stat.st_size,
            "mime_type": mime_type,
            "encoding": encoding,
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime,
            "extension": file_path.suffix.lower(),
        }
    
    async def cleanup_temp_files(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """
        Clean up temporary files older than specified age.
        
        Args:
            max_age_hours: Maximum age in hours for temp files.
            
        Returns:
            dict: Cleanup result.
        """
        try:
            import time
            
            deleted_count = 0
            deleted_size = 0
            cutoff_time = time.time() - (max_age_hours * 3600)
            
            for file_path in self.temp_dir.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_count += 1
                    deleted_size += file_size
            
            logger.info(
                f"Cleaned up {deleted_count} temp files ({deleted_size} bytes)"
            )
            
            return {
                "success": True,
                "deleted_files": deleted_count,
                "deleted_bytes": deleted_size,
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            stats = {
                "total_files": 0,
                "total_size": 0,
                "documents_count": 0,
                "thumbnails_count": 0,
                "temp_files_count": 0,
            }
            
            # Count documents
            for file_path in self.documents_dir.rglob("*"):
                if file_path.is_file():
                    stats["documents_count"] += 1
                    stats["total_files"] += 1
                    stats["total_size"] += file_path.stat().st_size
            
            # Count thumbnails
            for file_path in self.thumbnails_dir.rglob("*"):
                if file_path.is_file():
                    stats["thumbnails_count"] += 1
                    stats["total_files"] += 1
                    stats["total_size"] += file_path.stat().st_size
            
            # Count temp files
            for file_path in self.temp_dir.rglob("*"):
                if file_path.is_file():
                    stats["temp_files_count"] += 1
                    stats["total_files"] += 1
                    stats["total_size"] += file_path.stat().st_size
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {
                "error": str(e),
            }