from sqlmodel import SQLModel

from app.reservations.domain.movie_show_reservation import Movie, MovieShowReservation, SeatLocation


class MovieResponse(SQLModel):
    id: str
    title: str
    poster_image: str | None

    @classmethod
    def from_domain(cls, movie: Movie) -> "MovieResponse":
        return cls(id=movie.id, title=movie.title, poster_image=movie.poster_image)


class ReservedSeatResponse(SQLModel):
    row: int
    number: int

    @classmethod
    def from_domain(cls, seat: SeatLocation) -> "ReservedSeatResponse":
        return cls(row=seat.row, number=seat.number)


class MovieReservationResponse(SQLModel):
    reservation_id: str
    show_datetime: str
    movie: MovieResponse
    seats: list[ReservedSeatResponse]

    @classmethod
    def from_domain(cls, reservation: MovieShowReservation) -> "MovieReservationResponse":
        return cls(
            reservation_id=reservation.reservation_id,
            show_datetime=reservation.show_datetime.to_string(),
            movie=MovieResponse.from_domain(reservation.movie),
            seats=[ReservedSeatResponse.from_domain(seat) for seat in reservation.seats],
        )
