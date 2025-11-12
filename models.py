from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DownloadRequest(BaseModel):
    """Request model for download submission."""
    exchange: str = Field(..., description="Exchange name (e.g., binance)")
    data_types: List[str] = Field(default=["trades"], description="Data types to download")
    symbols: List[str] = Field(..., description="Trading symbols (e.g., BTC-USDT)")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    output_path: Optional[str] = Field(None, description="Custom output path")
    
    class Config:
        json_schema_extra = {
            "example": {
                "exchange": "binance",
                "data_types": ["trades"],
                "symbols": ["BTC-USDT", "ETH-USDT"],
                "start_date": "2024-01-01",
                "end_date": "2024-01-02",
                "output_path": "./datasets"
            }
        }


class JobResponse(BaseModel):
    """Response model for job information."""
    id: int
    status: JobStatus
    exchange: str
    data_types: List[str]
    symbols: List[str]
    start_date: str
    end_date: str
    output_path: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_by: str
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Response model for job list."""
    jobs: List[JobResponse]
    total: int


class JobSubmitResponse(BaseModel):
    """Response when a job is submitted."""
    job_id: int
    message: str
    status: JobStatus