from fastapi import UploadFile

from app.movies.domain.entities import PosterImage


def build_poster_image(uploaded_file: UploadFile | None) -> PosterImage | None:
    if uploaded_file is None:
        return None

    return PosterImage(
        filename=uploaded_file.filename,
        content=uploaded_file.file.read(),
        content_type=uploaded_file.content_type,
    )
