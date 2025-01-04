from collections.abc import Generator

import pytest

from app.settings import Settings, settings
from app.shared.infrastructure.storages.s3_storage import PublicMediaS3Storage


class TestPublicMediaS3Storage:
    @pytest.fixture
    def test_settings(self) -> Generator[Settings, None, None]:
        settings.AWS_ACCESS_KEY_ID = "access"
        settings.AWS_SECRET_ACCESS_KEY = "secret"
        settings.AWS_S3_BUCKET_NAME = "test"
        settings.AWS_S3_ENDPOINT_URL = "s3.amazonaws.com"
        yield settings

    @pytest.fixture
    def storage(self, test_settings: Settings) -> PublicMediaS3Storage:
        return PublicMediaS3Storage()

    def test_s3_storage_configuration(self, storage: PublicMediaS3Storage) -> None:
        assert storage.AWS_ACCESS_KEY_ID == "access"
        assert storage.AWS_SECRET_ACCESS_KEY == "secret"
        assert storage.AWS_S3_BUCKET_NAME == "test"
        assert storage.AWS_S3_ENDPOINT_URL == "s3.amazonaws.com"
        assert storage.AWS_DEFAULT_ACL == "public-read"
