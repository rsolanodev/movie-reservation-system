from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.payments.application.commands.confirm_payment import ConfirmPayment, ConfirmPaymentParams
from app.payments.domain.exceptions import ReservationNotFound
from app.payments.domain.finders.reservation_finder import ReservationFinder
from app.payments.domain.repositories.reservation_repository import ReservationRepository
from app.payments.domain.reservation import Reservation
from app.shared.domain.clients.payment_client import PaymentClient
from app.shared.domain.payment_event import PaymentEvent
from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.reservation_status import ReservationStatus


class TestConfirmPayment:
    @pytest.fixture
    def mock_reservation_repository(self) -> Any:
        return create_autospec(spec=ReservationRepository, spec_set=True, instance=True)

    @pytest.fixture
    def mock_reservation_finder(self) -> Any:
        return create_autospec(spec=ReservationFinder, spec_set=True, instance=True)

    @pytest.fixture
    def mock_payment_client(self) -> Any:
        return create_autospec(spec=PaymentClient, spec_set=True, instance=True)

    def test_confirms_reservation_when_payment_is_successful(
        self, mock_payment_client: Mock, mock_reservation_repository: Mock, mock_reservation_finder: Mock
    ) -> None:
        mock_payment_client.verify_payment.return_value = PaymentEvent(
            type="payment_intent.succeeded",
            payment_intent_id="test_provider_payment_id",
        )
        mock_reservation_finder.find_by_payment_id.return_value = Reservation(
            id=Id("3b74494d-0a95-49b1-91ef-bb211f802961"),
            status=ReservationStatus.PENDING,
        )

        ConfirmPayment(
            reservation_finder=mock_reservation_finder,
            reservation_repository=mock_reservation_repository,
            payment_client=mock_payment_client,
        ).execute(
            params=ConfirmPaymentParams(payload=b'{"type": "payment_intent.succeeded"}', signature="test_signature")
        )

        mock_payment_client.verify_payment.assert_called_once_with(
            payload=b'{"type": "payment_intent.succeeded"}', signature="test_signature"
        )
        mock_reservation_finder.find_by_payment_id.assert_called_once_with(
            provider_payment_id="test_provider_payment_id"
        )
        mock_reservation_repository.update.assert_called_once_with(
            reservation=Reservation(
                id=Id("3b74494d-0a95-49b1-91ef-bb211f802961"),
                status=ReservationStatus.CONFIRMED,
            )
        )

    @pytest.mark.parametrize(
        "payment_event_type, payload",
        [
            ("payment_intent.processing", b'{"type": "payment_intent.processing"}'),
            ("payment_intent.amount_capturable_updated", b'{"type": "payment_intent.amount_capturable_updated"}'),
            ("payment_intent.payment_failed", b'{"type": "payment_intent.payment_failed"}'),
        ],
    )
    def test_does_not_confirm_reservation_when_payment_is_not_successful(
        self,
        mock_payment_client: Mock,
        mock_reservation_repository: Mock,
        mock_reservation_finder: Mock,
        payment_event_type: str,
        payload: bytes,
    ) -> None:
        mock_payment_client.verify_payment.return_value = PaymentEvent(
            type=payment_event_type,
            payment_intent_id="test_provider_payment_id",
        )
        mock_reservation_finder.find_by_payment_id.return_value = Reservation(
            id=Id("3b74494d-0a95-49b1-91ef-bb211f802961"),
            status=ReservationStatus.PENDING,
        )

        ConfirmPayment(
            reservation_finder=mock_reservation_finder,
            reservation_repository=mock_reservation_repository,
            payment_client=mock_payment_client,
        ).execute(params=ConfirmPaymentParams(payload=payload, signature="test_signature"))

        mock_payment_client.verify_payment.assert_called_once_with(payload=payload, signature="test_signature")
        mock_reservation_finder.find_by_payment_id.assert_not_called()
        mock_reservation_repository.update.assert_not_called()

    def test_raises_reservation_not_found_exception_when_reservation_is_not_found(
        self, mock_payment_client: Mock, mock_reservation_repository: Mock, mock_reservation_finder: Mock
    ) -> None:
        mock_payment_client.verify_payment.return_value = PaymentEvent(
            type="payment_intent.succeeded",
            payment_intent_id="test_provider_payment_id",
        )
        mock_reservation_finder.find_by_payment_id.return_value = None

        with pytest.raises(ReservationNotFound):
            ConfirmPayment(
                reservation_finder=mock_reservation_finder,
                reservation_repository=mock_reservation_repository,
                payment_client=mock_payment_client,
            ).execute(
                params=ConfirmPaymentParams(payload=b'{"type": "payment_intent.succeeded"}', signature="test_signature")
            )
