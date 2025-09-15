"""
Aura Desktop Assistant - Versioning Service
Handles file versioning, command history, and state management for the .aura folder system.
"""

import os
import json
import hashlib
import shutil
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class OperationType(Enum):
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    MOVE = "move"
    COPY = "copy"


@dataclass
class FileVersion:
    """Represents a single file version"""
    id: str
    file_path: str
    timestamp: datetime
    size: int
    checksum: str
    change_description: str
    operation_type: OperationType
    command_id: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['operation_type'] = self.operation_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileVersion':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['operation_type'] = OperationType(data['operation_type'])
        return cls(**data)


@dataclass
class CommandHistoryEntry:
    """Represents a command execution in history"""
    id: str
    timestamp: datetime
    session_id: str
    user_input: str
    parsed_intent: Dict[str, Any]
    execution_duration: float
    success: bool
    error_message: Optional[str]
    affected_files: List[str]
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
    rollback_data: Optional[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandHistoryEntry':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class VersioningService:
    """Service for managing file versions and command history in .aura folder"""

    def __init__(self, root_path: Optional[str] = None):
        """Initialize versioning service

        Args:
            root_path: Root path for the application (defaults to current working directory)
        """
        self.root_path = Path(root_path) if root_path else Path.cwd()
        self.aura_path = self.root_path / ".aura"
        self.versions_path = self.aura_path / "versions"
        self.history_path = self.aura_path / "history"
        self.state_path = self.aura_path / "state"
        self.config_path = self.aura_path / "config"
        self.logs_path = self.aura_path / "logs"

        # Session tracking
        self.session_id = self._generate_session_id()

        logger.info("Versioning service initialized",
                    root_path=str(self.root_path),
                    aura_path=str(self.aura_path),
                    session_id=self.session_id)

    async def initialize_aura_folder(self) -> Dict[str, Any]:
        """Initialize .aura folder structure with proper permissions

        Returns:
            Dict containing initialization results and folder structure
        """
        try:
            logger.info("Initializing .aura folder structure")

            # Create main .aura directory
            self.aura_path.mkdir(exist_ok=True)

            # Create subdirectories
            subdirs = [
                self.versions_path,
                self.history_path,
                self.state_path / "checkpoints",
                self.state_path / "recovery",
                self.config_path,
                self.logs_path,
                self.history_path / "sessions"
            ]

            created_dirs = []
            for subdir in subdirs:
                if not subdir.exists():
                    subdir.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(
                        str(subdir.relative_to(self.root_path)))
                    logger.debug("Created directory", path=str(subdir))

            # Create initial configuration files
            await self._create_initial_config()

            # Create version index
            await self._initialize_version_index()

            # Create history index
            await self._initialize_history_index()

            # Create current state file
            await self._initialize_current_state()

            # Set appropriate permissions (read/write for owner only)
            await self._set_folder_permissions()

            result = {
                "success": True,
                "aura_path": str(self.aura_path),
                "created_directories": created_dirs,
                "session_id": self.session_id,
                "initialization_time": datetime.now(timezone.utc).isoformat(),
                "folder_structure": await self._get_folder_structure()
            }

            logger.info("Aura folder structure initialized successfully",
                        created_dirs=len(created_dirs),
                        session_id=self.session_id)

            return result

        except PermissionError as e:
            logger.error(
                "Permission denied creating .aura folder", error=str(e))
            raise PermissionError(f"Cannot create .aura folder: {str(e)}")
        except Exception as e:
            logger.error("Failed to initialize .aura folder", error=str(e))
            raise RuntimeError(f"Failed to initialize .aura folder: {str(e)}")

    async def create_file_version(self, file_path: str, change_description: str = "",
                                  operation_type: OperationType = OperationType.MODIFY,
                                  command_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a version backup of a file before modification

        Args:
            file_path: Path to the file to version
            change_description: Description of the change being made
            operation_type: Type of operation being performed
            command_id: ID of the command causing this version

        Returns:
            Dict containing version information
        """
        try:
            file_path = Path(file_path)

            # Ensure file exists
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Generate version ID and paths
            timestamp = datetime.now(timezone.utc)
            version_id = self._generate_version_id(file_path, timestamp)

            # Create file path hash for directory structure
            file_hash = self._hash_file_path(str(file_path))
            version_dir = self.versions_path / file_hash / version_id
            version_dir.mkdir(parents=True, exist_ok=True)

            # Copy file content
            content_path = version_dir / "content"
            shutil.copy2(file_path, content_path)

            # Calculate file metadata
            file_size = file_path.stat().st_size
            checksum = await self._calculate_file_checksum(file_path)

            # Create version metadata
            version = FileVersion(
                id=version_id,
                file_path=str(file_path),
                timestamp=timestamp,
                size=file_size,
                checksum=checksum,
                change_description=change_description,
                operation_type=operation_type,
                command_id=command_id or self._generate_command_id(),
                metadata={
                    "original_size": file_size,
                    "compression_ratio": 1.0,  # No compression initially
                    "is_differential": False,
                    "parent_version": None
                }
            )

            # Save version metadata
            metadata_path = version_dir / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(version.to_dict(), f, indent=2)

            # Update version index
            await self._update_version_index(version)

            logger.info("File version created successfully",
                        file_path=str(file_path),
                        version_id=version_id,
                        size=file_size)

            return {
                "version_id": version_id,
                "file_path": str(file_path),
                "timestamp": timestamp.isoformat(),
                "size": file_size,
                "checksum": checksum,
                "version_dir": str(version_dir),
                "operation_type": operation_type.value
            }

        except Exception as e:
            logger.error("Failed to create file version",
                         file_path=str(file_path), error=str(e))
            raise RuntimeError(f"Failed to create file version: {str(e)}")

    async def get_file_versions(self, file_path: str) -> List[Dict[str, Any]]:
        """Get all versions of a specific file

        Args:
            file_path: Path to the file

        Returns:
            List of version information dictionaries
        """
        try:
            file_hash = self._hash_file_path(file_path)
            file_versions_dir = self.versions_path / file_hash

            if not file_versions_dir.exists():
                return []

            versions = []
            for version_dir in file_versions_dir.iterdir():
                if version_dir.is_dir():
                    metadata_path = version_dir / "metadata.json"
                    if metadata_path.exists():
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            version_data = json.load(f)
                            versions.append(version_data)

            # Sort by timestamp (newest first)
            versions.sort(key=lambda x: x['timestamp'], reverse=True)

            logger.debug("Retrieved file versions",
                         file_path=file_path,
                         version_count=len(versions))

            return versions

        except Exception as e:
            logger.error("Failed to get file versions",
                         file_path=file_path, error=str(e))
            raise RuntimeError(f"Failed to get file versions: {str(e)}")

    async def restore_file_version(self, file_path: str, version_id: str) -> Dict[str, Any]:
        """Restore a file to a specific version

        Args:
            file_path: Path to the file to restore
            version_id: ID of the version to restore

        Returns:
            Dict containing restoration results
        """
        try:
            file_hash = self._hash_file_path(file_path)
            version_dir = self.versions_path / file_hash / version_id
            content_path = version_dir / "content"

            if not content_path.exists():
                raise FileNotFoundError(f"Version not found: {version_id}")

            # Create a new version of the current file before restoring
            if Path(file_path).exists():
                await self.create_file_version(
                    file_path,
                    f"Pre-restore backup before restoring to {version_id}",
                    OperationType.MODIFY
                )

            # Restore the file
            shutil.copy2(content_path, file_path)

            # Load version metadata
            metadata_path = version_dir / "metadata.json"
            with open(metadata_path, 'r', encoding='utf-8') as f:
                version_data = json.load(f)

            logger.info("File restored successfully",
                        file_path=file_path,
                        version_id=version_id,
                        original_timestamp=version_data['timestamp'])

            return {
                "success": True,
                "file_path": file_path,
                "restored_version_id": version_id,
                "restored_timestamp": version_data['timestamp'],
                "restoration_time": datetime.now(timezone.utc).isoformat()
            }

        except Exception as e:
            logger.error("Failed to restore file version",
                         file_path=file_path,
                         version_id=version_id,
                         error=str(e))
            raise RuntimeError(f"Failed to restore file version: {str(e)}")

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(
            str(datetime.now().timestamp()).encode()).hexdigest()[:8]
        return f"session_{timestamp}_{random_suffix}"

    def _generate_version_id(self, file_path: Path, timestamp: datetime) -> str:
        """Generate unique version ID"""
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S_%f")
        file_suffix = hashlib.md5(str(file_path).encode()).hexdigest()[:8]
        return f"{timestamp_str}_{file_suffix}"

    def _generate_command_id(self) -> str:
        """Generate unique command ID"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        return f"cmd_{timestamp}"

    def _hash_file_path(self, file_path: str) -> str:
        """Create hash of file path for directory structure"""
        return hashlib.sha256(file_path.encode('utf-8')).hexdigest()[:16]

    async def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    async def _create_initial_config(self):
        """Create initial configuration files"""
        # Retention policy configuration
        retention_config = {
            "file_versions": {
                "max_versions_per_file": 50,
                "max_age_days": 90,
                "max_storage_mb": 1000
            },
            "command_history": {
                "max_commands": 1000,
                "max_age_days": 30
            },
            "cleanup": {
                "auto_cleanup_enabled": True,
                "cleanup_interval_hours": 24
            }
        }

        retention_path = self.config_path / "retention.json"
        with open(retention_path, 'w', encoding='utf-8') as f:
            json.dump(retention_config, f, indent=2)

        # Storage configuration
        storage_config = {
            "compression_enabled": True,
            "differential_versioning": True,
            "encryption_enabled": False  # Can be enabled later
        }

        storage_path = self.config_path / "storage.json"
        with open(storage_path, 'w', encoding='utf-8') as f:
            json.dump(storage_config, f, indent=2)

        # Security configuration
        security_config = {
            "folder_permissions": "owner_only",
            "audit_logging": True,
            "secure_deletion": True
        }

        security_path = self.config_path / "security.json"
        with open(security_path, 'w', encoding='utf-8') as f:
            json.dump(security_config, f, indent=2)

    async def _initialize_version_index(self):
        """Create initial version index"""
        index_path = self.versions_path / "index.json"
        if not index_path.exists():
            initial_index = {
                "created": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "total_versions": 0,
                "files": {}
            }
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(initial_index, f, indent=2)

    async def _initialize_history_index(self):
        """Create initial history index"""
        index_path = self.history_path / "index.json"
        if not index_path.exists():
            initial_index = {
                "created": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "total_commands": 0,
                "sessions": {}
            }
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(initial_index, f, indent=2)

    async def _initialize_current_state(self):
        """Create initial current state file"""
        state_path = self.state_path / "current.json"
        if not state_path.exists():
            initial_state = {
                "created": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "session_id": self.session_id,
                "application_state": {},
                "active_files": []
            }
            with open(state_path, 'w', encoding='utf-8') as f:
                json.dump(initial_state, f, indent=2)

    async def _update_version_index(self, version: FileVersion):
        """Update the version index with new version"""
        index_path = self.versions_path / "index.json"

        # Load existing index
        with open(index_path, 'r', encoding='utf-8') as f:
            index = json.load(f)

        # Update index
        file_key = self._hash_file_path(version.file_path)
        if file_key not in index["files"]:
            index["files"][file_key] = {
                "file_path": version.file_path,
                "versions": [],
                "total_versions": 0
            }

        index["files"][file_key]["versions"].append({
            "version_id": version.id,
            "timestamp": version.timestamp.isoformat(),
            "size": version.size,
            "operation_type": version.operation_type.value
        })
        index["files"][file_key]["total_versions"] += 1
        index["total_versions"] += 1
        index["last_updated"] = datetime.now(timezone.utc).isoformat()

        # Save updated index
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)

    async def _set_folder_permissions(self):
        """Set appropriate permissions for .aura folder"""
        try:
            # On Windows, we'll rely on NTFS permissions
            # On Unix-like systems, set to 700 (owner read/write/execute only)
            if os.name != 'nt':
                os.chmod(self.aura_path, 0o700)
                for root, dirs, files in os.walk(self.aura_path):
                    for d in dirs:
                        os.chmod(os.path.join(root, d), 0o700)
                    for f in files:
                        os.chmod(os.path.join(root, f), 0o600)
        except Exception as e:
            logger.warning("Could not set folder permissions", error=str(e))

    async def _get_folder_structure(self) -> Dict[str, Any]:
        """Get the current .aura folder structure"""
        structure = {}

        def scan_directory(path: Path, relative_to: Path) -> Dict[str, Any]:
            result = {"type": "directory", "children": {}}
            try:
                for item in path.iterdir():
                    rel_path = str(item.relative_to(relative_to))
                    if item.is_dir():
                        result["children"][rel_path] = scan_directory(
                            item, relative_to)
                    else:
                        result["children"][rel_path] = {
                            "type": "file",
                            "size": item.stat().st_size
                        }
            except PermissionError:
                result["error"] = "Permission denied"
            return result

        if self.aura_path.exists():
            structure = scan_directory(self.aura_path, self.aura_path)

        return structure

    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics for .aura folder"""
        try:
            total_size = 0
            file_count = 0
            version_count = 0

            if self.aura_path.exists():
                for root, dirs, files in os.walk(self.aura_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(file_path)
                            total_size += size
                            file_count += 1

                            # Count versions
                            if "versions" in root and file == "content":
                                version_count += 1
                        except (OSError, IOError):
                            continue

            return {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count,
                "version_count": version_count,
                "aura_path": str(self.aura_path)
            }

        except Exception as e:
            logger.error("Failed to get storage stats", error=str(e))
            return {"error": str(e)}
