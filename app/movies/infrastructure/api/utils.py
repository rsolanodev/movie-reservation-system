from starlette.datastructures import UploadFile

from app.movies.domain.poster_image import PosterImage


def build_poster_image(uploaded_file: UploadFile | None) -> PosterImage | None:
    if isinstance(uploaded_file, UploadFile):
        return PosterImage(
            filename=uploaded_file.filename,
            file=uploaded_file.file,
        )
    return uploaded_file
