import asyncio
from pathlib import Path
from loguru import logger
from datetime import datetime
from typing import List

from tardis_dev import datasets

from app.config import settings
from app.database import db
from app.models import JobStatus
from app.telegram_notifier import notifier


class TardisDownloader:
    """Handles the actual download operations."""
    
    def __init__(self):
        self.api_key = settings.tardis_api_key
    
    async def download_data(
        self,
        job_id: int,
        exchange: str,
        data_types: List[str],
        symbols: List[str],
        start_date: str,
        end_date: str,
        output_path: str
    ):
        """
        Execute the download in a background task.
        This method handles the entire job lifecycle.
        """
        job = await db.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        try:
            # Update status to running
            await db.update_job_status(job_id, JobStatus.RUNNING)
            
            # Send Telegram notification
            await notifier.notify_job_started(
                job_id=job_id,
                exchange=exchange,
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                created_by=job.created_by
            )
            
            # Create output directory if it doesn't exist
            Path(output_path).mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Job {job_id}: Starting download")
            logger.info(f"  Exchange: {exchange}")
            logger.info(f"  Data types: {data_types}")
            logger.info(f"  Symbols: {symbols}")
            logger.info(f"  Date range: {start_date} to {end_date}")
            logger.info(f"  Output path: {output_path}")
            
            # Run the blocking download in a thread pool
            # This prevents blocking the async event loop
            await asyncio.to_thread(
                datasets.download,
                exchange=exchange,
                data_types=data_types,
                symbols=symbols,
                from_date=start_date,
                to_date=end_date,
                api_key=self.api_key,
                download_dir=output_path
            )
            
            # Calculate duration
            duration = None
            if job.started_at:
                duration = (datetime.utcnow() - job.started_at).total_seconds() / 60
            
            # Update status to completed
            await db.update_job_status(job_id, JobStatus.COMPLETED)
            
            # Send success notification
            await notifier.notify_job_completed(
                job_id=job_id,
                exchange=exchange,
                symbols=symbols,
                duration_minutes=duration
            )
            
            logger.success(f"Job {job_id}: Download completed successfully")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Job {job_id}: Download failed - {error_msg}")
            
            # Update status to failed
            await db.update_job_status(
                job_id,
                JobStatus.FAILED,
                error_message=error_msg
            )
            
            # Send failure notification
            await notifier.notify_job_failed(
                job_id=job_id,
                exchange=exchange,
                symbols=symbols,
                error=error_msg
            )


# Global downloader instance
downloader = TardisDownloader()