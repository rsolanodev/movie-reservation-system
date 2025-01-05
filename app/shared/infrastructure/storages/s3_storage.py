from fastapi_storages import S3Storage

from app.settings import get_settings


class PublicMediaS3Storage(S3Storage):  # type: ignore
    """
    S3 storage implementation for public media files.
    """

    AWS_DEFAULT_ACL: str = "public-read"

    def __init__(self) -> None:
        settings = get_settings()

        self.AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
        self.AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
        self.AWS_S3_BUCKET_NAME = settings.AWS_S3_BUCKET_NAME
        self.AWS_S3_ENDPOINT_URL = settings.AWS_S3_ENDPOINT_URL

        super().__init__()
