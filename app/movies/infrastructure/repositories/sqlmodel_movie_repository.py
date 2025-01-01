from app.movies.domain.movie import Movie
from app.movies.domain.repositories.movie_repository import MovieRepository
from app.movies.infrastructure.models import GenreModel, MovieModel
from app.shared.domain.value_objects.id import Id
from app.shared.infrastructure.repositories.sqlmodel_repository import SqlModelRepository


class SqlModelMovieRepository(MovieRepository, SqlModelRepository):
    def save(self, movie: Movie) -> None:
        movie_model = MovieModel.from_domain(movie=movie)
        self._session.merge(movie_model)
        self._session.commit()

    def get(self, id: Id) -> Movie | None:
        movie_model = self._session.get(MovieModel, id.to_uuid())

        if movie_model is None:
            return None

        movie = movie_model.to_domain()
        for genre in movie_model.genres:
            movie.add_genre(genre.to_domain())
        return movie

    def delete(self, id: Id) -> None:
        movie_model = self._session.get(MovieModel, id.to_uuid())
        self._session.delete(movie_model)
        self._session.commit()

    def add_genre(self, movie_id: Id, genre_id: Id) -> None:
        movie_model = self._session.get_one(MovieModel, movie_id.to_uuid())
        genre_model = self._session.get_one(GenreModel, genre_id.to_uuid())

        if genre_model not in movie_model.genres:
            movie_model.genres.append(genre_model)
            self._session.add(movie_model)
            self._session.commit()

    def remove_genre(self, movie_id: Id, genre_id: Id) -> None:
        movie_model = self._session.get_one(MovieModel, movie_id.to_uuid())
        genre_model = self._session.get_one(GenreModel, genre_id.to_uuid())

        if genre_model in movie_model.genres:
            movie_model.genres.remove(genre_model)
            self._session.add(movie_model)
            self._session.commit()
