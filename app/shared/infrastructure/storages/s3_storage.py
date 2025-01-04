from fastapi_storages import S3Storage

from app.settings import settings


class PublicMediaS3Storage(S3Storage):
    AWS_ACCESS_KEY_ID: str = settings.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY: str = settings.AWS_SECRET_ACCESS_KEY
    AWS_S3_BUCKET_NAME: str = settings.AWS_S3_BUCKET_NAME
    AWS_S3_ENDPOINT_URL: str = settings.AWS_S3_ENDPOINT_URL
    AWS_DEFAULT_ACL: str = "public-read"
