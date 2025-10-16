"""Configuration file for the project."""

import tempfile
from pathlib import Path
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ingestion Configuration
MAX_FILES = int(os.environ.get("GITINGEST_MAX_FILES", 1000))
MAX_TOTAL_SIZE_MB = int(os.environ.get("GITINGEST_MAX_TOTAL_SIZE_MB", 50))
MAX_TOTAL_SIZE_BYTES = MAX_TOTAL_SIZE_MB * 1024 * 1024
MAX_FILE_SIZE_MB = int(os.environ.get("GITINGEST_MAX_FILE_SIZE_MB", 1))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_DIRECTORY_DEPTH = int(os.environ.get("GITINGEST_MAX_DIRECTORY_DEPTH", 10))

OUTPUT_FILE_NAME = "digest.txt"

# Use /tmp directory as it's writable
TMP_BASE_PATH = Path(os.environ.get("TEMP_DIR", "/tmp/gitingest"))
os.makedirs(TMP_BASE_PATH, exist_ok=True)
