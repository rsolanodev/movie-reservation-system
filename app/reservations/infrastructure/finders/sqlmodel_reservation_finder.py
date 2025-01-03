from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select

from app.reservations.domain.finders.reservation_finder import ReservationFinder
from app.reservations.domain.movie_show_reservation import Movie, MovieShowReservation, SeatLocation
from app.reservations.domain.reservation import Reservation
from app.reservations.domain.seat import SeatStatus
from app.reservations.infrastructure.models import ReservationModel, SeatModel
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.shared.infrastructure.finders.sqlmodel_finder import SqlModelFinder
from app.showtimes.infrastructure.models import ShowtimeModel


class SqlModelReservationFinder(ReservationFinder, SqlModelFinder):
    def find_reservation(self, reservation_id: Id) -> Reservation:
        reservation_model = self._session.get_one(ReservationModel, reservation_id.to_uuid())
        return reservation_model.to_domain()

    def find_movie_show_reservations_by_user_id(self, user_id: Id) -> list[MovieShowReservation]:
        reservation_models = self._session.exec(
            select(ReservationModel)
            .options(
                joinedload(ReservationModel.showtime).joinedload(ShowtimeModel.movie),  # type: ignore
                selectinload(ReservationModel.seats),  # type: ignore
            )
            .where(
                ReservationModel.user_id == user_id.to_uuid(),
                ReservationModel.seats.any(SeatModel.status == SeatStatus.OCCUPIED),  # type: ignore
            )
        ).all()
        return self._sort_movie_show_reservations(
            [self._build_movie_show_reservation(reservation_model) for reservation_model in reservation_models]
        )

    def _build_movie_show_reservation(self, reservation_model: ReservationModel) -> MovieShowReservation:
        return MovieShowReservation(
            reservation_id=Id(reservation_model.id),
            show_datetime=DateTime.from_datetime(reservation_model.showtime.show_datetime),
            movie=Movie(
                id=Id(reservation_model.showtime.movie_id),
                title=reservation_model.showtime.movie.title,
                poster_image=reservation_model.showtime.movie.poster_image,
            ),
            seats=self._sort_reserved_seats(
                [SeatLocation(row=seat.row, number=seat.number) for seat in reservation_model.seats]
            ),
        )

    def _sort_movie_show_reservations(
        self, movie_show_reservations: list[MovieShowReservation]
    ) -> list[MovieShowReservation]:
        return sorted(movie_show_reservations, key=lambda msr: msr.show_datetime.value, reverse=True)

    def _sort_reserved_seats(self, seats: list[SeatLocation]) -> list[SeatLocation]:
        return sorted(seats, key=lambda seat: (seat.row, seat.number))
