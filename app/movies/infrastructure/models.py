import uuid

from sqlmodel import Field, Relationship, SQLModel

from app.movies.domain.entities import Category, Movie


class MovieCategoryLink(SQLModel, table=True):
    movie_id: uuid.UUID = Field(foreign_key="moviemodel.id", primary_key=True)
    category_id: uuid.UUID = Field(foreign_key="categorymodel.id", primary_key=True)


class MovieModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    description: str | None = None
    poster_image: str | None = None
    categories: list["CategoryModel"] = Relationship(
        back_populates="movies", link_model=MovieCategoryLink
    )

    @classmethod
    def from_domain(self, movie: Movie) -> "MovieModel":
        return MovieModel(
            id=movie.id,
            title=movie.title,
            description=movie.description,
            poster_image=movie.poster_image,
        )

    def to_domain(self) -> Movie:
        return Movie(
            id=self.id,
            title=self.title,
            description=self.description,
            poster_image=self.poster_image,
        )


class CategoryModel(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    movies: list[MovieModel] = Relationship(
        back_populates="categories", link_model=MovieCategoryLink
    )

    @classmethod
    def from_domain(cls, category: Category) -> "CategoryModel":
        return CategoryModel(id=category.id, name=category.name)
