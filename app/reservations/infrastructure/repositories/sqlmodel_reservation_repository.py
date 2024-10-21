from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select, update

from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.movie_reservation import Movie, MovieReservation, ReservedSeat
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.reservations.domain.reservation import Reservation
from app.reservations.domain.seat import SeatStatus
from app.reservations.infrastructure.models import ReservationModel, SeatModel
from app.shared.infrastructure.repositories.sqlmodel_repository import SqlModelRepository
from app.showtimes.infrastructure.models import ShowtimeModel


class SqlModelReservationRepository(ReservationRepository, SqlModelRepository):
    def create(self, reservation: Reservation) -> None:
        reservation_model = ReservationModel.from_domain(reservation)
        self._session.add(reservation_model)
        self._reserve_seats(reservation)
        self._session.commit()

    def _reserve_seats(self, reservation: Reservation) -> None:
        for seat in reservation.seats:
            seat_model = self._session.get_one(SeatModel, seat.id)
            seat_model.status = SeatStatus.RESERVED
            seat_model.reservation_id = reservation.id

    def find_seats(self, seat_ids: list[UUID]) -> Seats:
        seat_models = self._session.exec(
            select(SeatModel).filter(SeatModel.id.in_(seat_ids)),  # type: ignore
        ).all()
        return Seats([seat_model.to_domain() for seat_model in seat_models])

    def get(self, reservation_id: UUID) -> Reservation:
        reservation_model = self._session.get_one(ReservationModel, reservation_id)
        return reservation_model.to_domain()

    def release(self, reservation_id: UUID) -> None:
        self._session.exec(
            update(SeatModel)
            .where(SeatModel.reservation_id == reservation_id)  # type: ignore
            .values(status=SeatStatus.AVAILABLE, reservation_id=None)
        )
        self._session.commit()

    def find_by_user_id(self, user_id: UUID) -> list[MovieReservation]:
        reservation_models = self._session.exec(
            select(ReservationModel)
            .options(
                joinedload(ReservationModel.showtime).joinedload(ShowtimeModel.movie),  # type: ignore
                selectinload(ReservationModel.seats),  # type: ignore
            )
            .filter(
                ReservationModel.user_id == user_id,  # type: ignore
                ReservationModel.seats.any(SeatModel.status == SeatStatus.OCCUPIED),  # type: ignore
            )
        ).all()
        return self._sort_movie_reservations(
            [self._build_movie_reservation(reservation_model) for reservation_model in reservation_models]
        )

    def _build_movie_reservation(self, reservation_model: ReservationModel) -> MovieReservation:
        return MovieReservation(
            reservation_id=reservation_model.id,
            show_datetime=self._ensure_utc_timezone(reservation_model.showtime.show_datetime),
            movie=Movie(
                id=reservation_model.showtime.movie_id,
                title=reservation_model.showtime.movie.title,
                poster_image=reservation_model.showtime.movie.poster_image,
            ),
            seats=self._sort_reserved_seats(
                [ReservedSeat(row=seat.row, number=seat.number) for seat in reservation_model.seats]
            ),
        )

    def _sort_movie_reservations(self, movie_reservations: list[MovieReservation]) -> list[MovieReservation]:
        return sorted(movie_reservations, key=lambda movie_reservation: movie_reservation.show_datetime, reverse=True)

    def _sort_reserved_seats(self, seats: list[ReservedSeat]) -> list[ReservedSeat]:
        return sorted(seats, key=lambda seat: (seat.row, seat.number))

    def _ensure_utc_timezone(self, show_datetime: datetime) -> datetime:
        return show_datetime.replace(tzinfo=timezone.utc) if show_datetime.tzinfo is None else show_datetime
