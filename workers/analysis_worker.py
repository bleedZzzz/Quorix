"""Analysis and research intelligence worker."""

from __future__ import annotations

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
from app.dependencies import get_gap_service, get_job_service

logger = logging.getLogger("quorix.worker.analysis")


class AnalysisWorker:
    """Processes graph extraction, gap analysis, and review synthesis jobs."""

    def __init__(self) -> None:
        self.engine = create_engine(settings)
        self.session_factory = create_session_factory(self.engine)

    async def process_job(self, job_id_str: str, payload: dict) -> None:
        job_id = uuid.UUID(job_id_str)
        workspace_id = uuid.UUID(payload["workspace_id"])
        job_type = payload.get("job_type", "gap_analysis")

        async with self.session_factory() as session:
            job_svc = get_job_service(session)
            gap_svc = get_gap_service(session)

            try:
                await job_svc.update_progress(job_id, 0.2, f"Starting analysis: {job_type}")

                if job_type in ("gap_analysis", "gaps"):
                    paper_ids = [uuid.UUID(pid) for pid in payload.get("paper_ids", [])]
                    gaps = await gap_svc.analyze_gaps(workspace_id=workspace_id, paper_ids=paper_ids)
                    await job_svc.complete_job(
                        job_id,
                        {"status": "success", "gaps_count": len(gaps)},
                    )
                else:
                    await job_svc.complete_job(job_id, {"status": "unsupported_job_type"})

                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.exception("Failed processing analysis job %s", job_id)
                async with self.session_factory() as err_session:
                    err_job_svc = get_job_service(err_session)
                    await err_job_svc.fail_job(job_id, str(e))
                    await err_session.commit()

    async def close(self) -> None:
        await self.engine.dispose()
