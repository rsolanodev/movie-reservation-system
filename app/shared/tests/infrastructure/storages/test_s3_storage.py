from collections.abc import Generator
from unittest.mock import patch

import pytest

from app.settings import Settings
from app.shared.infrastructure.storages.s3_storage import PublicMediaS3Storage


class TestPublicMediaS3Storage:
    @pytest.fixture(autouse=True)
    def override_settings(self) -> Generator[None, None, None]:
        with patch(
            "app.shared.infrastructure.storages.s3_storage.settings",
            Settings(
                AWS_ACCESS_KEY_ID="access",
                AWS_SECRET_ACCESS_KEY="secret",
                AWS_S3_BUCKET_NAME="test",
                AWS_S3_ENDPOINT_URL="s3.amazonaws.com",
            ),
        ):
            yield

    def test_s3_storage_configuration(self) -> None:
        storage = PublicMediaS3Storage()
        assert storage.AWS_ACCESS_KEY_ID == "access"
        assert storage.AWS_SECRET_ACCESS_KEY == "secret"
        assert storage.AWS_S3_BUCKET_NAME == "test"
        assert storage.AWS_S3_ENDPOINT_URL == "s3.amazonaws.com"
        assert storage.AWS_DEFAULT_ACL == "public-read"
