from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest

from app.settings import Settings
from app.shared.infrastructure.storages.s3_storage import S3Storage


class TestS3Storage:
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

    @pytest.fixture
    def mock_boto3(self) -> Generator[Mock, None, None]:
        with patch("app.shared.infrastructure.storages.s3_storage.boto3") as mock:
            yield mock

    def test_client_is_configured_with_correct_settings(self, mock_boto3: Mock) -> None:
        S3Storage()

        mock_boto3.client.assert_called_once_with(
            service_name="s3",
            endpoint_url="https://s3.amazonaws.com",
            aws_access_key_id="access",
            aws_secret_access_key="secret",
        )
