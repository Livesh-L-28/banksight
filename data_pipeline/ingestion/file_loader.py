"""
BankSight Data Ingestion & Safe File Loading Module
Handles CSV and Excel file ingestion with strict extension, size, and encoding safety checks.
"""

import os
from pathlib import Path
from typing import Tuple, Optional
import pandas as pd

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
DEFAULT_MAX_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


class FileLoader:
    def __init__(self, max_size_bytes: int = DEFAULT_MAX_SIZE_BYTES):
        self.max_size_bytes = max_size_bytes

    def validate_file_metadata(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Validates file exists, has safe extension, and does not exceed size limit."""
        if not file_path.exists():
            return False, f"File not found: {file_path}"

        suffix = file_path.suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            return False, f"Invalid file extension '{suffix}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"

        size_bytes = file_path.stat().st_size
        if size_bytes > self.max_size_bytes:
            return False, f"File size ({size_bytes / (1024*1024):.2f} MB) exceeds maximum limit of {self.max_size_bytes / (1024*1024):.1f} MB."

        if size_bytes == 0:
            return False, "File is empty (0 bytes)."

        return True, None

    def load_tabular_data(self, file_path: Path) -> pd.DataFrame:
        """Safely loads CSV or Excel into a pandas DataFrame."""
        is_valid, error_msg = self.validate_file_metadata(file_path)
        if not is_valid:
            raise ValueError(error_msg)

        suffix = file_path.suffix.lower()
        if suffix == ".csv":
            try:
                return pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                return pd.read_csv(file_path, encoding="latin1")
        elif suffix in [".xlsx", ".xls"]:
            return pd.read_excel(file_path, engine="openpyxl" if suffix == ".xlsx" else None)
        else:
            raise ValueError(f"Unsupported format: {suffix}")
