from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, JSON
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager

from app.config import settings
from app.models import JobStatus


class Base(DeclarativeBase):
    pass


class DownloadJob(Base):
    """Database model for download jobs."""
    __tablename__ = "download_jobs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(20), default=JobStatus.PENDING.value)
    exchange: Mapped[str] = mapped_column(String(50))
    data_types: Mapped[List[str]] = mapped_column(JSON)
    symbols: Mapped[List[str]] = mapped_column(JSON)
    start_date: Mapped[str] = mapped_column(String(20))
    end_date: Mapped[str] = mapped_column(String(20))
    output_path: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(100))


class Database:
    """Database manager for async operations."""
    
    def __init__(self):
        self.engine = create_async_engine(
            settings.database_url,
            echo=False,
            future=True
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def init_db(self):
        """Initialize database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    @asynccontextmanager
    async def get_session(self):
        """Get async database session."""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def create_job(
        self,
        exchange: str,
        data_types: List[str],
        symbols: List[str],
        start_date: str,
        end_date: str,
        output_path: str,
        created_by: str
    ) -> DownloadJob:
        """Create a new download job."""
        async with self.get_session() as session:
            job = DownloadJob(
                exchange=exchange,
                data_types=data_types,
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                output_path=output_path,
                created_by=created_by,
                status=JobStatus.PENDING.value
            )
            session.add(job)
            await session.flush()
            await session.refresh(job)
            return job
    
    async def get_job(self, job_id: int) -> Optional[DownloadJob]:
        """Get a job by ID."""
        async with self.get_session() as session:
            return await session.get(DownloadJob, job_id)
    
    async def get_all_jobs(self, limit: int = 100) -> List[DownloadJob]:
        """Get all jobs ordered by creation date."""
        from sqlalchemy import select
        async with self.get_session() as session:
            result = await session.execute(
                select(DownloadJob)
                .order_by(DownloadJob.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())
    
    async def update_job_status(
        self,
        job_id: int,
        status: JobStatus,
        error_message: Optional[str] = None
    ):
        """Update job status."""
        async with self.get_session() as session:
            job = await session.get(DownloadJob, job_id)
            if job:
                job.status = status.value
                if status == JobStatus.RUNNING and not job.started_at:
                    job.started_at = datetime.utcnow()
                elif status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                    job.completed_at = datetime.utcnow()
                if error_message:
                    job.error_message = error_message
    
    async def close(self):
        """Close database connections."""
        await self.engine.dispose()


# Global database instance
db = Database()