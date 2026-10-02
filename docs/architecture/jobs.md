# Quorix — Background Jobs Architecture

## Principle

Long-running work must never block HTTP requests. All expensive operations run in background workers connected via Redis queue.

---

## Architecture

```
FastAPI API
    │
    ▼
Redis Queue (job dispatch)
    │
    ▼
Worker Process(es)
    ├── Ingestion Worker
    │   ├── PDF download
    │   ├── PDF parsing
    │   ├── Page extraction
    │   ├── Section detection
    │   ├── Metadata extraction
    │   ├── Reference extraction
    │   ├── Semantic chunking
    │   ├── Embedding generation
    │   ├── Vector indexing
    │   ├── Lexical indexing
    │   └── Quality validation
    │
    ├── Analysis Worker
    │   ├── Deep paper analysis
    │   ├── Graph extraction
    │   ├── Gap analysis
    │   └── Literature review synthesis
    │
    └── Common
        ├── Job management
        ├── Progress tracking
        ├── Error handling
        └── Retry logic
```

---

## Job Model

### States

```
queued → running → completed
                 → failed → retrying → running → ...
                 → cancelled
```

| State       | Description                               |
|------------|-------------------------------------------|
| `queued`   | Job is in the queue, waiting for a worker |
| `running`  | Worker is actively processing             |
| `completed`| Successfully finished                     |
| `failed`   | Encountered an error                      |
| `retrying` | Scheduled for retry after failure         |
| `cancelled`| Manually cancelled                        |

### Job Record

```python
class Job(Base):
    id: UUID
    workspace_id: UUID
    job_type: str           # ingestion, parsing, embedding, analysis, etc.
    status: str             # queued, running, completed, failed, retrying, cancelled
    payload: dict           # Job-specific input data
    result: dict | None     # Job output on completion
    error: str | None       # Error message on failure
    progress: float         # 0.0 → 1.0
    retry_count: int
    max_retries: int
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
```

### Job Events

```python
class JobEvent(Base):
    id: UUID
    job_id: UUID
    event_type: str     # started, progress, step_completed, warning, error, completed
    message: str | None
    data: dict | None
    created_at: datetime
```

---

## Job Types

### Phase 1 (Foundation)

| Job Type         | Description                              | Trigger          |
|-----------------|------------------------------------------|------------------|
| `paper_import`  | Download PDF from URL, store in object storage | Paper import API |

### Phase 2 (Papers)

| Job Type            | Description                              | Trigger          |
|--------------------|------------------------------------------|------------------|
| `pdf_parse`        | Extract pages, text, structure from PDF  | After import     |
| `metadata_extract` | Extract paper metadata from PDF content  | After parsing    |

### Phase 3 (RAG)

| Job Type           | Description                                | Trigger         |
|-------------------|--------------------------------------------|-----------------|
| `semantic_chunk`  | Split document into semantic chunks         | After parsing   |
| `embed_chunks`    | Generate embeddings for all chunks          | After chunking  |
| `vector_index`    | Index embeddings into Qdrant                | After embedding |
| `lexical_index`   | Index text into PostgreSQL full-text search | After parsing   |

### Phase 6+ (Intelligence)

| Job Type             | Description                               | Trigger         |
|---------------------|-------------------------------------------|-----------------|
| `deep_analysis`     | Generate deep paper analysis              | User request    |
| `graph_extraction`  | Extract knowledge graph entities/relations | After ingestion |
| `gap_analysis`      | Analyze corpus for research gaps          | User request    |
| `review_synthesis`  | Synthesize literature review              | User request    |

---

## Ingestion Pipeline

The full paper ingestion is a multi-step pipeline job:

```
paper_import
    ↓
pdf_parse
    ↓
metadata_extract
    ↓
semantic_chunk
    ↓
embed_chunks
    ↓
vector_index + lexical_index
    ↓
quality_validation
    ↓
ready
```

Each step updates:
- Job `progress` (0.0 → 1.0)
- Job `status`
- Job events log
- Paper `status` (imported → ingesting → ready / failed)

---

## Worker Implementation

### Worker Process

```python
class Worker:
    """Background worker that processes jobs from Redis queue."""

    async def start(self):
        """Start consuming jobs from the queue."""

    async def process_job(self, job_id: UUID):
        """Process a single job with error handling and progress tracking."""

    async def handle_failure(self, job_id: UUID, error: Exception):
        """Handle job failure with retry logic."""
```

### Job Handler Interface

```python
class JobHandler(ABC):
    """Base interface for job type handlers."""

    @abstractmethod
    async def execute(self, job: Job, context: WorkerContext) -> dict:
        """Execute the job and return the result."""

    @abstractmethod
    def job_type(self) -> str:
        """Return the job type this handler processes."""
```

---

## Retry Strategy

- **Max retries:** Configurable per job type (default: 3)
- **Backoff:** Exponential with jitter
- **Idempotency:** Jobs should be designed to be safely retried
- **Dead letter:** After max retries, job moves to `failed` with full error context

```python
def calculate_backoff(retry_count: int) -> float:
    """Exponential backoff with jitter."""
    base_delay = 2 ** retry_count  # 1s, 2s, 4s, 8s, ...
    jitter = random.uniform(0, base_delay * 0.1)
    return min(base_delay + jitter, 300)  # Cap at 5 minutes
```

---

## Progress Reporting

Jobs emit progress events that the API can relay to the frontend:

```python
# Worker side
await job_context.report_progress(
    progress=0.4,
    message="Extracting page 12 of 30",
    data={"current_page": 12, "total_pages": 30}
)

# API side (polling or SSE)
GET /api/v1/jobs/{job_id}
GET /api/v1/jobs/{job_id}/events
```

---

## Redis Queue Design

### Queue Keys

```
quorix:jobs:queue          — Main job queue (FIFO)
quorix:jobs:processing     — Currently processing jobs
quorix:jobs:delayed        — Delayed retry jobs
quorix:jobs:dead           — Dead letter queue
```

### Job Dispatch

```python
async def enqueue_job(
    workspace_id: UUID,
    job_type: str,
    payload: dict,
    priority: int = 0,
) -> Job:
    """Create a job record in PostgreSQL and enqueue it in Redis."""
```

---

## Concurrency & Scaling

- Workers can be horizontally scaled (multiple worker containers)
- Each worker processes one job at a time (simple, reliable)
- Job locking via Redis to prevent duplicate processing
- Worker heartbeat for stuck job detection
- Graceful shutdown: finish current job before stopping

---

## Monitoring

All job lifecycle events are logged:
- Job creation, start, progress, completion, failure, retry
- Worker health and queue depth
- Structured JSON logging with `job_id`, `workspace_id`, `job_type`

API endpoints expose:
- Active/recent jobs per workspace
- Job details and event history
- Queue depth (admin)
