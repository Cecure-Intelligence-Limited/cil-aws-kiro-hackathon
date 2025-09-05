"""
File system operations service
Handles file creation, opening, and cross-platform operations
"""

import os
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
import structlog

from config import settings

logger = structlog.get_logger(__name__)


class FileService:
    """Service for file system operations"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.safe_dirs = [Path(d).resolve() for d in settings.SAFE_DIRECTORIES]
        
        # Ensure safe directories exist
        for safe_dir in self.safe_dirs:
            safe_dir.mkdir(parents=True, exist_ok=True)
    
    def _validate_path(self, path: str) -> Path:
        """Validate and resolve file path for security"""
        
        # Convert to Path object
        file_path = Path(path)
        
        # Check for path traversal
        if '..' in str(file_path):
            raise ValueError("Path traversal not allowed")
        
        # If it's a relative path, make it relative to the first safe directory
        if not file_path.is_absolute():
            file_path = self.safe_dirs[0] / file_path
        
        # Resolve the path
        file_path = file_path.resolve()
        
        # Ensure path is within safe directories
        is_safe = any(
            str(file_path).startswith(str(safe_dir)) 
            for safe_dir in self.safe_dirs
        )
        
        if not is_safe:
            # If not in safe dirs, put it in the first safe directory
            file_path = self.safe_dirs[0] / file_path.name
        
        return file_path
    
    def _validate_file_size(self, file_path: Path) -> None:
        """Check if file size is within limits"""
        if file_path.exists():
            size = file_path.stat().st_size
            if size > settings.MAX_FILE_SIZE:
                raise ValueError(f"File size ({size} bytes) exceeds maximum allowed ({settings.MAX_FILE_SIZE} bytes)")
    
    def _validate_file_extension(self, file_path: Path) -> None:
        """Check if file extension is allowed"""
        extension = file_path.suffix.lower()
        if extension and extension not in settings.ALLOWED_FILE_EXTENSIONS:
            raise ValueError(f"File extension '{extension}' not allowed. Allowed: {settings.ALLOWED_FILE_EXTENSIONS}")
    
    async def create_file(self, title: str, path: Optional[str] = None, content: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new file with optional content
        
        Args:
            title: Name of the file to create
            path: Optional directory path
            content: Optional file content
            
        Returns:
            Dictionary with file creation details
        """
        
        try:
            # Determine full file path
            if path:
                full_path = Path(path) / title
            else:
                full_path = Path(title)
            
            # Validate and secure the path
            secure_path = self._validate_path(str(full_path))
            
            # Validate file extension
            self._validate_file_extension(secure_path)
            
            # Check if file already exists
            if secure_path.exists():
                raise FileExistsError(f"File already exists: {secure_path}")
            
            # Ensure parent directory exists
            secure_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            content = content or ""
            secure_path.write_text(content, encoding='utf-8')
            
            # Validate file size after creation
            self._validate_file_size(secure_path)
            
            logger.info("File created successfully", 
                       file_path=str(secure_path),
                       size=len(content))
            
            return {
                "file_path": str(secure_path),
                "size": len(content),
                "created": True,
                "directory": str(secure_path.parent)
            }
            
        except Exception as e:
            logger.error("Failed to create file", title=title, path=path, error=str(e))
            raise
    
    async def open_item(self, query: str, item_type: str = "auto") -> Dict[str, Any]:
        """
        Open a file, application, or folder using cross-platform methods
        
        Args:
            query: Search query for the item to open
            item_type: Type of item (file, application, folder, auto)
            
        Returns:
            Dictionary with open operation details
        """
        
        try:
            logger.info("Attempting to open item", query=query, type=item_type)
            
            # Try to find the item
            found_path = await self._find_item(query, item_type)
            
            if found_path:
                # Open the found item
                await self._open_path(found_path)
                
                return {
                    "path": str(found_path),
                    "type": self._detect_item_type(found_path),
                    "opened": True,
                    "method": "file_system"
                }
            else:
                # Try to open as application
                if item_type in ["application", "auto"]:
                    success = await self._open_application(query)
                    if success:
                        return {
                            "query": query,
                            "type": "application",
                            "opened": True,
                            "method": "application_launcher"
                        }
                
                raise FileNotFoundError(f"Could not find or open: {query}")
                
        except Exception as e:
            logger.error("Failed to open item", query=query, error=str(e))
            raise
    
    async def _find_item(self, query: str, item_type: str) -> Optional[Path]:
        """Find item in file system"""
        
        # Search in safe directories
        for safe_dir in self.safe_dirs:
            if not safe_dir.exists():
                continue
                
            # Direct path match
            direct_path = safe_dir / query
            if direct_path.exists():
                return direct_path
            
            # Fuzzy search in directory
            try:
                for item in safe_dir.rglob("*"):
                    if query.lower() in item.name.lower():
                        # Type filtering
                        if item_type == "file" and item.is_file():
                            return item
                        elif item_type == "folder" and item.is_dir():
                            return item
                        elif item_type == "auto":
                            return item
            except (PermissionError, OSError):
                continue
        
        # Search in common locations
        common_paths = [
            Path.home() / "Desktop",
            Path.home() / "Documents",
            Path.home() / "Downloads",
            Path.cwd()
        ]
        
        for common_path in common_paths:
            if not common_path.exists():
                continue
                
            try:
                for item in common_path.iterdir():
                    if query.lower() in item.name.lower():
                        if item_type == "file" and item.is_file():
                            return item
                        elif item_type == "folder" and item.is_dir():
                            return item
                        elif item_type == "auto":
                            return item
            except (PermissionError, OSError):
                continue
        
        return None
    
    async def _open_path(self, path: Path) -> None:
        """Open file or folder using system default application"""
        
        try:
            if self.system == "windows":
                os.startfile(str(path))
            elif self.system == "darwin":  # macOS
                subprocess.run(["open", str(path)], check=True)
            else:  # Linux and others
                subprocess.run(["xdg-open", str(path)], check=True)
                
            logger.info("Opened path successfully", path=str(path))
            
        except subprocess.CalledProcessError as e:
            logger.error("Failed to open path", path=str(path), error=str(e))
            raise
        except Exception as e:
            logger.error("Failed to open path", path=str(path), error=str(e))
            raise
    
    async def _open_application(self, app_name: str) -> bool:
        """Try to open application by name"""
        
        try:
            if self.system == "windows":
                # Try common Windows application patterns
                app_patterns = [
                    app_name,
                    f"{app_name}.exe",
                    app_name.replace(" ", "")
                ]
                
                for pattern in app_patterns:
                    try:
                        subprocess.run(["start", "", pattern], shell=True, check=True)
                        logger.info("Opened Windows application", app=pattern)
                        return True
                    except subprocess.CalledProcessError:
                        continue
                        
            elif self.system == "darwin":  # macOS
                # Try to open macOS application
                try:
                    subprocess.run(["open", "-a", app_name], check=True)
                    logger.info("Opened macOS application", app=app_name)
                    return True
                except subprocess.CalledProcessError:
                    pass
                    
            else:  # Linux
                # Try common Linux application launchers
                launchers = ["which", "whereis"]
                for launcher in launchers:
                    try:
                        result = subprocess.run([launcher, app_name], 
                                              capture_output=True, text=True, check=True)
                        if result.stdout.strip():
                            subprocess.run([app_name], check=True)
                            logger.info("Opened Linux application", app=app_name)
                            return True
                    except subprocess.CalledProcessError:
                        continue
            
            return False
            
        except Exception as e:
            logger.error("Failed to open application", app=app_name, error=str(e))
            return False
    
    def _detect_item_type(self, path: Path) -> str:
        """Detect the type of item"""
        if path.is_file():
            return "file"
        elif path.is_dir():
            return "folder"
        else:
            return "unknown"