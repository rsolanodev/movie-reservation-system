from app.movies.domain.finders.genre_finder import GenreFinder
from app.movies.domain.genre import Genre


class RetrieveGenres:
    def __init__(self, finder: GenreFinder) -> None:
        self._finder = finder

    def execute(self) -> list[Genre]:
        return self._finder.find_all()
