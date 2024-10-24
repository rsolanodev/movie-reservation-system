from datetime import timedelta
from typing import Any
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest

from app.reservations.application.create_reservation import CreateReservation, CreateReservationParams
from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.exceptions import SeatsNotAvailable
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.reservations.domain.reservation import Reservation
from app.reservations.domain.schedulers.reservation_release_scheduler import ReservationReleaseScheduler
from app.reservations.domain.seat import Seat, SeatStatus


class TestCreateReservation:
    @pytest.fixture
    def mock_repository(self) -> Any:
        return create_autospec(ReservationRepository, instance=True)

    @pytest.fixture
    def mock_reservation_release_scheduler(self) -> Any:
        return create_autospec(ReservationReleaseScheduler, instance=True)

    def test_creates_reservation(self, mock_repository: Mock, mock_reservation_release_scheduler: Mock) -> None:
        mock_repository.find_seats.return_value = Seats(
            [
                Seat(id=UUID("c555276e-0be4-48ea-9e27-fe1500384380"), row=1, number=1, status=SeatStatus.AVAILABLE),
                Seat(id=UUID("bb07c2f1-33f4-4987-ad02-8a420104f810"), row=1, number=2, status=SeatStatus.AVAILABLE),
            ]
        )

        reservation = CreateReservation(
            repository=mock_repository, reservation_release_scheduler=mock_reservation_release_scheduler
        ).execute(
            params=CreateReservationParams(
                showtime_id=UUID("aa7a9372-09a0-415a-8c65-ec5aa6026e72"),
                seat_ids=[UUID("c555276e-0be4-48ea-9e27-fe1500384380"), UUID("bb07c2f1-33f4-4987-ad02-8a420104f810")],
                user_id=UUID("1553d340-89eb-433b-a101-981bdaa740ed"),
            )
        )

        mock_repository.find_seats.assert_called_once_with(
            seat_ids=[UUID("c555276e-0be4-48ea-9e27-fe1500384380"), UUID("bb07c2f1-33f4-4987-ad02-8a420104f810")]
        )
        mock_repository.create.assert_called_once_with(
            reservation=Reservation(
                id=reservation.id,
                user_id=UUID("1553d340-89eb-433b-a101-981bdaa740ed"),
                showtime_id=UUID("aa7a9372-09a0-415a-8c65-ec5aa6026e72"),
                has_paid=False,
                seats=Seats(
                    [
                        Seat(
                            id=UUID("c555276e-0be4-48ea-9e27-fe1500384380"),
                            row=1,
                            number=1,
                            status=SeatStatus.AVAILABLE,
                        ),
                        Seat(
                            id=UUID("bb07c2f1-33f4-4987-ad02-8a420104f810"),
                            row=1,
                            number=2,
                            status=SeatStatus.AVAILABLE,
                        ),
                    ]
                ),
            )
        )
        mock_reservation_release_scheduler.schedule.assert_called_once_with(
            reservation_id=reservation.id, delay=timedelta(minutes=15)
        )

    @pytest.mark.parametrize("seat_status", [SeatStatus.RESERVED, SeatStatus.OCCUPIED])
    def test_does_not_create_reservation_when_seats_are_not_available(
        self, mock_repository: Mock, mock_reservation_release_scheduler: Mock, seat_status: SeatStatus
    ) -> None:
        mock_repository.find_seats.return_value = Seats(
            [
                Seat(id=UUID("c555276e-0be4-48ea-9e27-fe1500384380"), row=1, number=1, status=SeatStatus.AVAILABLE),
                Seat(id=UUID("bb07c2f1-33f4-4987-ad02-8a420104f810"), row=1, number=2, status=seat_status),
            ]
        )

        with pytest.raises(SeatsNotAvailable):
            CreateReservation(
                repository=mock_repository, reservation_release_scheduler=mock_reservation_release_scheduler
            ).execute(
                params=CreateReservationParams(
                    showtime_id=UUID("aa7a9372-09a0-415a-8c65-ec5aa6026e72"),
                    seat_ids=[
                        UUID("c555276e-0be4-48ea-9e27-fe1500384380"),
                        UUID("bb07c2f1-33f4-4987-ad02-8a420104f810"),
                    ],
                    user_id=UUID("1553d340-89eb-433b-a101-981bdaa740ed"),
                )
            )

        mock_repository.find_seats.assert_called_once_with(
            seat_ids=[UUID("c555276e-0be4-48ea-9e27-fe1500384380"), UUID("bb07c2f1-33f4-4987-ad02-8a420104f810")]
        )
        mock_repository.create.assert_not_called()
        mock_reservation_release_scheduler.schedule.assert_not_called()
