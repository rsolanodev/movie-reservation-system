from app.reservations.domain.reservation import Reservation
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id


class Reservations(list[Reservation]):
    @property
    def ids(self) -> list[Id]:
        return [reservation.id for reservation in self]

    def expired(self, expiration_datetime: DateTime) -> "Reservations":
        return Reservations([reservation for reservation in self if reservation.created_at < expiration_datetime])
