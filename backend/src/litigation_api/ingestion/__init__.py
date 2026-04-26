"""Ingestion package for source adapters and normalization logic."""
from .client import CRLCAClient, CRLCAClientError
from .pipeline import IngestionPipeline

__all__ = ["CRLCAClient", "CRLCAClientError", "IngestionPipeline"]
