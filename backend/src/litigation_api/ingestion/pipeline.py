import logging
import asyncio
import boto3
from typing import Optional, Tuple, List
from botocore.exceptions import ClientError

from ..models.domain import Case, DocketEntry, Document
from .crlca_models import CRLCACase, CRLCADocket, CRLCADocument
from .normalization import normalize_case, normalize_docket_entry, normalize_document
from .client import CRLCAClient

logger = logging.getLogger(__name__)

SUPPORTED_DOCUMENT_TYPES = {"Complaint", "Opinion/Order", "Settlement"}

class IngestionPipeline:
    def __init__(self, s3_endpoint_url: str, s3_bucket_name: str, client: Optional[CRLCAClient] = None):
        self.s3_endpoint_url = s3_endpoint_url
        self.s3_bucket_name = s3_bucket_name
        self.client = client
        self.s3_client = boto3.client("s3", endpoint_url=self.s3_endpoint_url)

    def _ensure_bucket_sync(self):
        """Ensure the target S3 bucket exists (synchronous)."""
        try:
            self.s3_client.head_bucket(Bucket=self.s3_bucket_name)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            # Handle "404", "403" and "NoSuchBucket" as absent bucket indications
            if error_code in ("404", "403", "NoSuchBucket"):
                logger.info(f"Bucket {self.s3_bucket_name} not found or inaccessible. Creating it.")
                try:
                    self.s3_client.create_bucket(Bucket=self.s3_bucket_name)
                except ClientError as ce:
                    ce_code = ce.response.get("Error", {}).get("Code")
                    if ce_code == "BucketAlreadyOwnedByYou":
                        pass # Ignore if we already own it
                    else:
                        raise
            else:
                raise

    async def _ensure_bucket_async(self):
        """Asynchronously ensure the target S3 bucket exists."""
        await asyncio.to_thread(self._ensure_bucket_sync)

    def _upload_raw_artifact(self, doc_id: str, content: bytes) -> str:
        """Upload raw document content to S3-compatible storage and return object key.
        This is a synchronous method and should be run in an executor.
        """
        object_key = f"raw/{doc_id}.pdf"
        self.s3_client.put_object(
            Bucket=self.s3_bucket_name,
            Key=object_key,
            Body=content,
            ContentType="application/pdf"
        )
        logger.info(f"Uploaded raw artifact to {self.s3_bucket_name}/{object_key}")
        return object_key

    async def fetch_and_normalize_case(self, case_id: int) -> Tuple[Case, List[DocketEntry], List[Document]]:
        """Fetch a single case, its dockets and documents, and normalize them."""

        await self._ensure_bucket_async()

        # We need to ensure self.client is initialized and has an active context
        async def _do_work(active_client: CRLCAClient) -> Tuple[Case, List[DocketEntry], List[Document]]:
            # 1. Fetch Case
            raw_case_dict = await active_client.fetch_case_details(case_id)
            raw_case = CRLCACase(**raw_case_dict)
            domain_case = normalize_case(raw_case)

            # 2. Fetch Dockets
            domain_dockets = []
            async for raw_docket_dict in active_client.fetch_case_dockets(case_id):
                raw_docket = CRLCADocket(**raw_docket_dict)
                domain_dockets.append(normalize_docket_entry(raw_docket, domain_case.case_id))

            # 3. Fetch Documents
            domain_documents = []
            async for raw_document_dict in active_client.fetch_case_documents(case_id):
                raw_document = CRLCADocument(**raw_document_dict)

                # Documents need a reference to a docket entry.
                # In CRLCA v2.1 API, we usually just associate documents to the main case/docket,
                # but if we don't have a specific docket link, we use the first docket or a dummy one.
                entry_id = domain_dockets[0].entry_id if domain_dockets else f"crlca_docket_unknown_{case_id}"

                domain_doc = normalize_document(raw_document, domain_case.case_id, entry_id)

                # Check document type support
                if domain_doc.document_type in SUPPORTED_DOCUMENT_TYPES and raw_document.file:
                    logger.info(f"Downloading supported document: {domain_doc.doc_id}")
                    try:
                        file_content = await active_client.download_file(raw_document.file)
                    except Exception as e:
                        logger.error(f"Failed to download file for document {domain_doc.doc_id}: {e}")
                        domain_doc.ingestion_status = "FAILED_DOWNLOAD"
                        domain_documents.append(domain_doc)
                        continue

                    try:
                        # Run the blocking S3 upload in a separate thread
                        await asyncio.to_thread(self._upload_raw_artifact, domain_doc.doc_id, file_content)
                        domain_doc.ingestion_status = "INGESTED"
                    except Exception as e:
                        logger.error(f"Failed to upload file for document {domain_doc.doc_id}: {e}")
                        domain_doc.ingestion_status = "FAILED_UPLOAD"
                else:
                    logger.info(f"Skipping download for unsupported document type or missing file URL: {domain_doc.doc_id} ({domain_doc.document_type})")
                    domain_doc.ingestion_status = "SKIPPED_UNSUPPORTED_TYPE" # Adhere to unsupported document fallback behavior

                domain_documents.append(domain_doc)

            return domain_case, domain_dockets, domain_documents

        if self.client:
            return await _do_work(self.client)
        else:
            async with CRLCAClient() as client:
                return await _do_work(client)
