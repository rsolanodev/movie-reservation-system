from collections.abc import Generator
from datetime import datetime
from typing import Any
from unittest.mock import ANY, Mock, create_autospec, patch

import pytest
from freezegun import freeze_time

from app.reservations.application.commands.create_reservation import CreateReservation, CreateReservationParams
from app.reservations.domain.collections.seats import Seats
from app.reservations.domain.exceptions import SeatsNotAvailable
from app.reservations.domain.finders.seat_finder import SeatFinder
from app.reservations.domain.repositories.reservation_repository import ReservationRepository
from app.reservations.domain.reservation import Reservation
from app.reservations.domain.seat import Seat
from app.settings import Settings
from app.shared.domain.clients.payment_client import PaymentClient
from app.shared.domain.payment_intent import PaymentIntent
from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.reservation_status import ReservationStatus
from app.shared.domain.value_objects.seat_status import SeatStatus


@freeze_time("2025-01-10T12:00:00Z")
class TestCreateReservation:
    @pytest.fixture
    def mock_reservation_repository(self) -> Any:
        return create_autospec(spec=ReservationRepository, instance=True, spec_set=True)

    @pytest.fixture
    def mock_seat_finder(self) -> Any:
        return create_autospec(spec=SeatFinder, instance=True, spec_set=True)

    @pytest.fixture
    def mock_payment_client(self) -> Any:
        return create_autospec(spec=PaymentClient, instance=True, spec_set=True)

    @pytest.fixture(autouse=True)
    def override_settings(self) -> Generator[None, None, None]:
        with patch(
            "app.reservations.application.commands.create_reservation.settings",
            Settings(GENERAL_ADMISSION_PRICE=15.0),
        ):
            yield

    def test_creates_reservation(
        self, mock_reservation_repository: Mock, mock_seat_finder: Mock, mock_payment_client: Mock
    ) -> None:
        mock_seat_finder.find_seats.return_value = Seats(
            [
                Seat(id=Id("c555276e-0be4-48ea-9e27-fe1500384380"), row=1, number=1, status=SeatStatus.AVAILABLE),
                Seat(id=Id("bb07c2f1-33f4-4987-ad02-8a420104f810"), row=1, number=2, status=SeatStatus.AVAILABLE),
            ]
        )
        mock_payment_client.create_payment_intent.return_value = PaymentIntent(
            client_secret="test_client_secret",
            provider_payment_id="pi_3MtwBwLkdIwHu7ix28a3tqPa",
            amount=30.0,
        )

        CreateReservation(
            reservation_repository=mock_reservation_repository,
            seat_finder=mock_seat_finder,
            payment_client=mock_payment_client,
        ).execute(
            params=CreateReservationParams(
                showtime_id=Id("aa7a9372-09a0-415a-8c65-ec5aa6026e72"),
                seat_ids=[Id("c555276e-0be4-48ea-9e27-fe1500384380"), Id("bb07c2f1-33f4-4987-ad02-8a420104f810")],
                user_id=Id("1553d340-89eb-433b-a101-981bdaa740ed"),
            )
        )

        mock_seat_finder.find_seats.assert_called_once_with(
            seat_ids=[Id("c555276e-0be4-48ea-9e27-fe1500384380"), Id("bb07c2f1-33f4-4987-ad02-8a420104f810")]
        )
        mock_payment_client.create_payment_intent.assert_called_once_with(amount=30.0)
        mock_reservation_repository.create.assert_called_once_with(
            reservation=Reservation(
                id=ANY,
                user_id=Id("1553d340-89eb-433b-a101-981bdaa740ed"),
                showtime_id=Id("aa7a9372-09a0-415a-8c65-ec5aa6026e72"),
                status=ReservationStatus.PENDING,
                seats=Seats(
                    [
                        Seat(
                            id=Id("c555276e-0be4-48ea-9e27-fe1500384380"),
                            row=1,
                            number=1,
                            status=SeatStatus.AVAILABLE,
                        ),
                        Seat(
                            id=Id("bb07c2f1-33f4-4987-ad02-8a420104f810"),
                            row=1,
                            number=2,
                            status=SeatStatus.AVAILABLE,
                        ),
                    ]
                ),
                provider_payment_id="pi_3MtwBwLkdIwHu7ix28a3tqPa",
                created_at=DateTime.from_datetime(datetime(2025, 1, 10, 12, 0, 0)),
            )
        )

    @pytest.mark.parametrize("seat_status", [SeatStatus.RESERVED, SeatStatus.OCCUPIED])
    def test_does_not_create_reservation_when_seats_are_not_available(
        self,
        mock_reservation_repository: Mock,
        mock_seat_finder: Mock,
        mock_payment_client: Mock,
        seat_status: SeatStatus,
    ) -> None:
        mock_seat_finder.find_seats.return_value = Seats(
            [
                Seat(id=Id("c555276e-0be4-48ea-9e27-fe1500384380"), row=1, number=1, status=SeatStatus.AVAILABLE),
                Seat(id=Id("bb07c2f1-33f4-4987-ad02-8a420104f810"), row=1, number=2, status=seat_status),
            ]
        )

        with pytest.raises(SeatsNotAvailable):
            CreateReservation(
                reservation_repository=mock_reservation_repository,
                seat_finder=mock_seat_finder,
                payment_client=mock_payment_client,
            ).execute(
                params=CreateReservationParams(
                    showtime_id=Id("aa7a9372-09a0-415a-8c65-ec5aa6026e72"),
                    seat_ids=[
                        Id("c555276e-0be4-48ea-9e27-fe1500384380"),
                        Id("bb07c2f1-33f4-4987-ad02-8a420104f810"),
                    ],
                    user_id=Id("1553d340-89eb-433b-a101-981bdaa740ed"),
                )
            )

        mock_seat_finder.find_seats.assert_called_once_with(
            seat_ids=[Id("c555276e-0be4-48ea-9e27-fe1500384380"), Id("bb07c2f1-33f4-4987-ad02-8a420104f810")]
        )
        mock_payment_client.create_payment_intent.assert_not_called()
        mock_reservation_repository.create.assert_not_called()
