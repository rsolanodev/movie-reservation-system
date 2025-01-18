from app.shared.infrastructure.storages.s3_storage import S3Storage


class MoviePosterS3Storage(S3Storage):
    storage_path: str = "movies/posters/"
    acl_policy: str = "public-read"
