import json
import boto3
from typing import Optional
from botocore.exceptions import ClientError
from .models import ParsedArtifact

class ArtifactStorage:
    def __init__(self, bucket_name: str, endpoint_url: Optional[str] = None):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3', endpoint_url=endpoint_url)

    def _get_key(self, doc_id: str) -> str:
        return f"parsed/{doc_id}.json"

    def store_artifact(self, artifact: ParsedArtifact) -> str:
        key = self._get_key(artifact.doc_id)
        payload = artifact.model_dump_json()
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=payload.encode('utf-8'),
            ContentType='application/json'
        )
        return key

    def get_artifact(self, doc_id: str) -> Optional[ParsedArtifact]:
        key = self._get_key(doc_id)
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            payload = response['Body'].read().decode('utf-8')
            return ParsedArtifact.model_validate_json(payload)
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code')
            status_code = e.response.get('ResponseMetadata', {}).get('HTTPStatusCode')
            if error_code == 'NoSuchKey' or status_code == 404:
                return None
            raise
