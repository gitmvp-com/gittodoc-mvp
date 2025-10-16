"""This module contains functions for cloning a Git repository to a local path."""

import os
import logging
from pathlib import Path
from typing import Optional
import asyncio

from gitingest.schemas import CloneConfig

TIMEOUT: int = 60

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def clone_repo(config: CloneConfig) -> None:
    """Clone a repository to a local path."""
    
    url: str = config.url
    local_path: str = config.local_path
    branch: Optional[str] = config.branch
    
    logger.info(f"Starting clone of repository: {url} to path: {local_path}")
    
    # Create parent directory if it doesn't exist
    parent_dir = Path(local_path).parent
    try:
        os.makedirs(parent_dir, exist_ok=True)
    except OSError as exc:
        raise OSError(f"Failed to create parent directory {parent_dir}: {exc}") from exc
    
    # Build clone command
    clone_cmd = ["git", "clone", "--single-branch", "--depth=1"]
    
    if branch and branch.lower() not in ("main", "master"):
        clone_cmd += ["--branch", branch]
    
    clone_cmd += [url, local_path]
    
    logger.info(f"Running clone command: {' '.join(clone_cmd)}")
    
    # Clone the repository
    proc = await asyncio.create_subprocess_exec(
        *clone_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=TIMEOUT)
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError(f"Clone operation timed out after {TIMEOUT} seconds")
    
    if proc.returncode != 0:
        error_message = stderr.decode().strip()
        logger.error(f"Clone command failed: {error_message}")
        raise RuntimeError(f"Clone failed: {error_message}")
    
    logger.info("Repository cloned successfully")
