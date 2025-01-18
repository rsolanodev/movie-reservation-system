from io import BytesIO
from typing import BinaryIO
from unittest.mock import Mock

import pytest

from app.movies.infrastructure.storages.movie_poster_s3_storage import MoviePosterS3Storage
from app.shared.tests.infrastructure.storages.test_s3_storage import TestS3Storage


class TestMoviePosterS3Storage(TestS3Storage):
    @pytest.fixture
    def poster_image(self) -> BinaryIO:
        return BytesIO(b"poster image content")

    def test_upload_movie_poster_image(self, mock_boto3: Mock, poster_image: BinaryIO) -> None:
        key = MoviePosterS3Storage().upload_file(file=poster_image, name="nosferatu.png")

        mock_boto3.client.return_value.upload_fileobj.assert_called_once_with(
            FileObj=poster_image,
            Bucket="test",
            Key="movies/posters/nosferatu.png",
            ExtraArgs={"ACL": "public-read", "ContentType": "image/png"},
        )

        assert key == "movies/posters/nosferatu.png"
