# Worker Package

This package contains the worker code for processing data asynchronously, specifically parsing documents as part of the case-shift data ingestion pipeline.

## Structure
* `src/worker/parsing/models.py`: Defines the data models for parsed artifacts (`ParsedArtifact`, `ParsedPage`)
* `src/worker/parsing/storage.py`: Handles saving and loading parsed artifacts to an S3-compatible object store under the `/parsed/` layout
* `src/worker/parsing/parser.py`: Contains a dummy parser protocol and implementation for text extraction

## Testing
Run tests from the `worker` directory:
```bash
uv run pytest tests/
```
