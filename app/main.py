from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Optional, List
from loguru import logger
import sys

from app.config import settings
from app.database import db
from app.models import (
    DownloadRequest,
    JobResponse,
    JobListResponse,
    JobSubmitResponse,
    JobStatus
)
from app.downloader import downloader


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/app.log",
    rotation="100 MB",
    retention="30 days",
    level="INFO"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Download Service API")
    await db.init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down Download Service API")
    await db.close()


app = FastAPI(
    title="Tardis Download Service",
    description="API for managing Tardis data downloads",
    version="1.0.0",
    lifespan=lifespan
)


def verify_api_token(x_api_token: Optional[str] = Header(None)):
    """Verify API token if configured."""
    if settings.api_token:
        if not x_api_token or x_api_token != settings.api_token:
            raise HTTPException(status_code=401, detail="Invalid or missing API token")
    return True


def verify_user(x_username: Optional[str] = Header(None)):
    """Verify that the requesting user is allowed."""
    if not x_username:
        raise HTTPException(
            status_code=400,
            detail="Missing X-Username header. Please provide your username."
        )
    
    if not settings.is_user_allowed(x_username):
        raise HTTPException(
            status_code=403,
            detail=f"User '{x_username}' is not authorized to use this service"
        )
    
    return x_username


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Tardis Download Service",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "telegram": "configured"
    }


@app.post("/download", response_model=JobSubmitResponse, status_code=202)
async def submit_download(
    request: DownloadRequest,
    background_tasks: BackgroundTasks,
    username: str = Depends(verify_user),
    _: bool = Depends(verify_api_token)
):
    """
    Submit a new download job.
    
    The download will run in the background and you'll receive Telegram notifications.
    """
    try:
        # Use default output path if not provided
        output_path = request.output_path or settings.default_output_path
        
        # Create job in database
        job = await db.create_job(
            exchange=request.exchange,
            data_types=request.data_types,
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            output_path=output_path,
            created_by=username
        )
        
        # Add download task to background
        background_tasks.add_task(
            downloader.download_data,
            job_id=job.id,
            exchange=request.exchange,
            data_types=request.data_types,
            symbols=request.symbols,
            start_date=request.start_date,
            end_date=request.end_date,
            output_path=output_path
        )
        
        logger.info(f"Job {job.id} submitted by {username}")
        
        return JobSubmitResponse(
            job_id=job.id,
            message=f"Download job submitted successfully. You'll receive Telegram notifications.",
            status=JobStatus.PENDING
        )
        
    except Exception as e:
        logger.error(f"Error submitting job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    limit: int = 50,
    username: str = Depends(verify_user),
    _: bool = Depends(verify_api_token)
):
    """
    Get list of all download jobs.
    
    Returns the most recent jobs first.
    """
    try:
        jobs = await db.get_all_jobs(limit=limit)
        
        job_responses = [
            JobResponse(
                id=job.id,
                status=JobStatus(job.status),
                exchange=job.exchange,
                data_types=job.data_types,
                symbols=job.symbols,
                start_date=job.start_date,
                end_date=job.end_date,
                output_path=job.output_path,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                error_message=job.error_message,
                created_by=job.created_by
            )
            for job in jobs
        ]
        
        return JobListResponse(
            jobs=job_responses,
            total=len(job_responses)
        )
        
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    username: str = Depends(verify_user),
    _: bool = Depends(verify_api_token)
):
    """
    Get details of a specific job.
    """
    try:
        job = await db.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return JobResponse(
            id=job.id,
            status=JobStatus(job.status),
            exchange=job.exchange,
            data_types=job.data_types,
            symbols=job.symbols,
            start_date=job.start_date,
            end_date=job.end_date,
            output_path=job.output_path,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error_message=job.error_message,
            created_by=job.created_by
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/{job_id}/status")
async def get_job_status(
    job_id: int,
    username: str = Depends(verify_user),
    _: bool = Depends(verify_api_token)
):
    """
    Quick endpoint to check job status.
    """
    try:
        job = await db.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        return {
            "job_id": job.id,
            "status": job.status,
            "created_by": job.created_by,
            "created_at": job.created_at,
            "error_message": job.error_message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status {job_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False
    )