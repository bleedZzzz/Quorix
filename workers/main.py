"""Main worker execution loop."""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add apps/api to sys.path
api_path = Path(__file__).resolve().parent.parent / "apps" / "api"
if str(api_path) not in sys.path:
    sys.path.insert(0, str(api_path))

from app.config.settings import settings
from workers.analysis_worker import AnalysisWorker
from workers.common.queue import JobQueue
from workers.ingestion_worker import IngestionWorker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("quorix.worker")


async def run_worker() -> None:
    queue = JobQueue(redis_url=settings.redis_url)
    ingestion_worker = IngestionWorker()
    analysis_worker = AnalysisWorker()

    stop_event = asyncio.Event()

    def handle_stop():
        logger.info("Stopping worker loop...")
        stop_event.set()

    loop = asyncio.get_running_loop()
    try:
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, handle_stop)
    except NotImplementedError:
        # On Windows add_signal_handler may not be implemented for SIGINT
        pass

    logger.info("Quorix Background Worker started. Listening on %s...", queue.queue_name)

    try:
        while not stop_event.is_set():
            try:
                job_data = await queue.dequeue(timeout=2)
                if not job_data:
                    await asyncio.sleep(0.5)
                    continue

                job_id = job_data["job_id"]
                job_type = job_data["job_type"]
                payload = job_data["payload"]

                logger.info("Processing job %s (type: %s)", job_id, job_type)

                if job_type in ("ingestion", "pdf_ingestion"):
                    await ingestion_worker.process_job(job_id, payload)
                elif job_type in ("analysis", "gap_analysis", "graph"):
                    await analysis_worker.process_job(job_id, payload)
                else:
                    logger.warning("Unknown job type: %s", job_type)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in worker polling loop: %s", e)
                await asyncio.sleep(1.0)
    finally:
        await queue.close()
        await ingestion_worker.close()
        await analysis_worker.close()
        logger.info("Worker gracefully terminated.")


if __name__ == "__main__":
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        pass
