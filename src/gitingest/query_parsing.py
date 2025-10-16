"""Parse and validate repository queries."""

import hashlib
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from gitingest.config import MAX_FILE_SIZE_BYTES, TMP_BASE_PATH
from gitingest.schemas import IngestionQuery


async def parse_query(
    source: str,
    max_file_size: int = MAX_FILE_SIZE_BYTES,
    from_web: bool = False,
    include_patterns: Optional[str] = None,
    ignore_patterns: Optional[str] = None,
) -> IngestionQuery:
    """Parse a repository URL or path into an IngestionQuery."""
    
    # Clean up the source
    source = source.strip()
    
    # Parse GitHub URL
    url_pattern = r"(?:https?://)?(?:www\.)?github\.com/([^/]+)/([^/]+)(?:/.*)?$"
    match = re.match(url_pattern, source)
    
    if not match:
        raise ValueError(f"Invalid GitHub URL: {source}")
    
    owner, repo = match.groups()
    repo = repo.replace(".git", "")
    
    url = f"https://github.com/{owner}/{repo}"
    slug = f"{owner}/{repo}"
    
    # Generate unique ID for this query
    query_id = hashlib.md5(source.encode()).hexdigest()[:8]
    
    # Create local path for cloning
    local_path = TMP_BASE_PATH / query_id
    
    # Parse patterns
    include_set = set(include_patterns.split(",")) if include_patterns else None
    ignore_set = set(ignore_patterns.split(",")) if ignore_patterns else None
    
    return IngestionQuery(
        id=query_id,
        url=url,
        local_path=local_path,
        slug=slug,
        max_file_size=max_file_size,
        include_patterns=include_set,
        ignore_patterns=ignore_set,
    )
