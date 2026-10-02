"""Ingestion worker process."""

from __future__ import annotations

import asyncio
import logging
import sys
import uuid
from pathlib import Path

# Add apps/api to sys.path to access domain services
api_path = Path(__file__).resolve().parent.parent / "apps" / "api"
if str(api_path) not in sys.path:
    sys.path.insert(0, str(api_path))

from app.config.settings import settings
from app.infrastructure.database.engine import create_engine
from app.infrastructure.database.session import create_session_factory
from app.dependencies import get_ingestion_service, get_job_service

logger = logging.getLogger("quorix.worker.ingestion")


class IngestionWorker:
    """Processes PDF ingestion, parsing, chunking, and embedding jobs."""

    def __init__(self) -> None:
        self.engine = create_engine(settings)
        self.session_factory = create_session_factory(self.engine)

    async def process_job(self, job_id_str: str, payload: dict) -> None:
        job_id = uuid.UUID(job_id_str)
        workspace_id = uuid.UUID(payload["workspace_id"])
        paper_id = uuid.UUID(payload["paper_id"])

        async with self.session_factory() as session:
            job_svc = get_job_service(session)
            ingest_svc = get_ingestion_service(session)

            try:
                await job_svc.update_progress(job_id, 0.1, "Starting PDF ingestion worker")

                if "pdf_url" in payload:
                    await ingest_svc.ingest_from_url(
                        workspace_id=workspace_id,
                        paper_id=paper_id,
                        pdf_url=payload["pdf_url"],
                    )
                await job_svc.complete_job(job_id, {"status": "success", "paper_id": str(paper_id)})
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.exception("Failed processing ingestion job %s", job_id)
                async with self.session_factory() as err_session:
                    err_job_svc = get_job_service(err_session)
                    await err_job_svc.fail_job(job_id, str(e))
                    await err_session.commit()

    async def close(self) -> None:
        await self.engine.dispose()
