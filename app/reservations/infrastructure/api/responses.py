from sqlmodel import SQLModel

from app.reservations.domain.movie_show_reservation import Movie, MovieShowReservation, SeatLocation
from app.shared.domain.payment_intent import PaymentIntent


class MovieResponse(SQLModel):
    id: str
    title: str
    poster_image: str | None

    @classmethod
    def from_domain(cls, movie: Movie) -> "MovieResponse":
        return cls(id=movie.id, title=movie.title, poster_image=movie.poster_image)


class SeatResponse(SQLModel):
    row: int
    number: int

    @classmethod
    def from_domain(cls, seat: SeatLocation) -> "SeatResponse":
        return cls(row=seat.row, number=seat.number)


class ReservationResponse(SQLModel):
    reservation_id: str
    show_datetime: str
    movie: MovieResponse
    seats: list[SeatResponse]

    @classmethod
    def from_domain(cls, reservation: MovieShowReservation) -> "ReservationResponse":
        return cls(
            reservation_id=reservation.reservation_id,
            show_datetime=reservation.show_datetime.to_string(),
            movie=MovieResponse.from_domain(reservation.movie),
            seats=[SeatResponse.from_domain(seat) for seat in reservation.seats],
        )

    @classmethod
    def from_domain_list(cls, reservations: list[MovieShowReservation]) -> list["ReservationResponse"]:
        return [cls.from_domain(reservation) for reservation in reservations]


class PaymentIntentResponse(SQLModel):
    client_secret: str
    provider_payment_id: str
    amount: float

    @classmethod
    def from_domain(cls, payment_intent: PaymentIntent) -> "PaymentIntentResponse":
        return cls(
            client_secret=payment_intent.client_secret,
            provider_payment_id=payment_intent.provider_payment_id,
            amount=payment_intent.amount,
        )
