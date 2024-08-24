from starlette.datastructures import UploadFile

from app.core.domain.constants.unset import UnsetType
from app.movies.domain.entities import PosterImage


def build_poster_image(
    uploaded_file: UploadFile | None | UnsetType,
) -> PosterImage | None | UnsetType:
    if isinstance(uploaded_file, UploadFile):
        return PosterImage(
            filename=uploaded_file.filename,
            content=uploaded_file.file.read(),
            content_type=uploaded_file.content_type,
        )
    return uploaded_file
