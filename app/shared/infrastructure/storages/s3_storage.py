import mimetypes
from typing import BinaryIO

import boto3

from app.settings import get_settings
from app.shared.domain.storages.storage import Storage

settings = get_settings()


class S3Storage(Storage):
    def __init__(self) -> None:
        self._client = boto3.client(
            service_name="s3",
            endpoint_url=f"https://{settings.AWS_S3_ENDPOINT_URL}",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    def upload_file(self, file: BinaryIO, name: str) -> str:
        file.seek(0)
        key = f"{self.storage_path}{name}"
        content_type, _ = mimetypes.guess_type(key)

        self._client.upload_fileobj(
            FileObj=file,
            Bucket=settings.AWS_S3_BUCKET_NAME,
            Key=key,
            ExtraArgs={
                "ACL": self.acl_policy,
                "ContentType": content_type or self.fallback_content_type,
            },
        )
        return key
