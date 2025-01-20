from dataclasses import dataclass

from app.reservations.domain.exceptions import SeatsNotAvailable
from app.reservations.domain.finders.seat_finder import SeatFinder
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.reservations.domain.reservation import Reservation
from app.settings import get_settings
from app.shared.domain.clients.payment_client import PaymentClient
from app.shared.domain.payment_intent import PaymentIntent
from app.shared.domain.value_objects.id import Id

settings = get_settings()


@dataclass(frozen=True)
class CreateReservationParams:
    showtime_id: Id
    seat_ids: list[Id]
    user_id: Id


class CreateReservation:
    def __init__(
        self, reservation_repository: ReservationRepository, seat_finder: SeatFinder, payment_client: PaymentClient
    ) -> None:
        self._reservation_repository = reservation_repository
        self._seat_finder = seat_finder
        self._payment_client = payment_client

    def execute(self, params: CreateReservationParams) -> PaymentIntent:
        seats = self._seat_finder.find_seats(seat_ids=params.seat_ids)

        if not seats.are_available():
            raise SeatsNotAvailable()

        total_amount = seats.calculate_total_price(settings.GENERAL_ADMISSION_PRICE)
        payment_intent = self._payment_client.create_payment_intent(amount=total_amount)

        reservation = Reservation.create(user_id=params.user_id, showtime_id=params.showtime_id, seats=seats)
        reservation.assign_payment_id(payment_intent.provider_payment_id)
        self._reservation_repository.create(reservation=reservation)

        return payment_intent
