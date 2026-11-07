"""
Data Pipeline & Quality Audit Entities: DataImportJob, DataQualityResult.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text
from backend.database.connection import Base


class DataImportJob(Base):
    __tablename__ = "data_import_jobs"

    job_id = Column(String(50), primary_key=True)
    file_name = Column(String(200), nullable=False)
    file_format = Column(String(20), nullable=False)  # CSV, XLSX
    file_size_bytes = Column(Integer, nullable=False)
    status = Column(String(30), default="Pending", nullable=False)  # Pending, Processing, Completed, Failed
    records_processed = Column(Integer, default=0, nullable=False)
    records_succeeded = Column(Integer, default=0, nullable=False)
    records_rejected = Column(Integer, default=0, nullable=False)
    error_summary = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)


class DataQualityResult(Base):
    __tablename__ = "data_quality_results"

    check_id = Column(String(50), primary_key=True)
    job_id = Column(String(50), nullable=True)
    check_name = Column(String(100), nullable=False)  # e.g., NullCheck, DuplicateCheck, RangeCheck
    target_table = Column(String(50), nullable=False)
    target_column = Column(String(50), nullable=True)
    total_evaluated = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    failure_rate_pct = Column(Float, default=0.0, nullable=False)
    status = Column(String(20), default="Passed", nullable=False)  # Passed, Warning, Failed
    details = Column(JSON, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
