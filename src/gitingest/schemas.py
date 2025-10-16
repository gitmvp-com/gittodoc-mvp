"""Data schemas for gitingest."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional


class FileSystemNodeType(str, Enum):
    """Enumeration for file system node types."""
    FILE = "file"
    DIRECTORY = "directory"
    SYMLINK = "symlink"


@dataclass
class FileSystemNode:
    """Represents a node in the file system tree."""
    name: str
    type: FileSystemNodeType
    path_str: str
    path: Path
    size: int = 0
    file_count: int = 0
    dir_count: int = 0
    depth: int = 0
    children: List["FileSystemNode"] = field(default_factory=list)
    content: Optional[str] = None

    def __post_init__(self):
        """Load file content if this is a file node."""
        if self.type == FileSystemNodeType.FILE and self.path.exists():
            try:
                self.content = self.path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                self.content = "[Binary or unreadable file]"

    def sort_children(self) -> None:
        """Sort children: directories first, then files, alphabetically."""
        self.children.sort(key=lambda x: (x.type != FileSystemNodeType.DIRECTORY, x.name.lower()))


@dataclass
class FileSystemStats:
    """Statistics for file system traversal."""
    total_files: int = 0
    total_size: int = 0


@dataclass
class CloneConfig:
    """Configuration for cloning a repository."""
    url: str
    local_path: str
    commit: Optional[str] = None
    branch: Optional[str] = None
    subpath: str = "/"
    blob: bool = False


@dataclass
class IngestionQuery:
    """Query parameters for repository ingestion."""
    id: str
    url: str
    local_path: Path
    slug: str
    subpath: str = "/"
    max_file_size: int = 1024 * 1024  # 1MB default
    include_patterns: Optional[set] = None
    ignore_patterns: Optional[set] = None
    branch: Optional[str] = None
    commit: Optional[str] = None
    type: Optional[str] = None

    def extract_clone_config(self) -> CloneConfig:
        """Extract clone configuration from query."""
        return CloneConfig(
            url=self.url,
            local_path=str(self.local_path),
            commit=self.commit,
            branch=self.branch,
            subpath=self.subpath,
            blob=self.type == "blob"
        )
