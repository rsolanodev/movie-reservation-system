from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest

from app.payments.application.commands.refund_payment import RefundPaymentParams
from app.payments.application.subscribers.refund_when_reservation_cancelled import RefundWhenReservationCancelled
from app.reservations.domain.events import ReservationCancelled


class TestRefundWhenReservationCancelled:
    @pytest.fixture
    def mock_refund_payment(self) -> Generator[Mock, None, None]:
        with patch("app.payments.application.subscribers.refund_when_reservation_cancelled.RefundPayment") as mock:
            yield mock

    @pytest.fixture
    def mock_stripe_client(self) -> Generator[Mock, None, None]:
        with patch("app.payments.application.subscribers.refund_when_reservation_cancelled.StripeClient") as mock:
            yield mock.return_value

    def test_has_correct_event_class_and_action(self) -> None:
        subscriber = RefundWhenReservationCancelled()
        assert subscriber.event_class == ReservationCancelled
        assert subscriber.action == "refund"

    def test_calls_refund_payment(self, mock_refund_payment: Mock, mock_stripe_client: Mock) -> None:
        RefundWhenReservationCancelled().on(
            ReservationCancelled(reservation_id="test_reservation_id", provider_payment_id="test_payment_id")
        )

        mock_refund_payment.assert_called_once_with(payment_client=mock_stripe_client)
        mock_refund_payment.return_value.execute.assert_called_once_with(
            RefundPaymentParams(reservation_id="test_reservation_id", provider_payment_id="test_payment_id")
        )

    def test_does_not_call_refund_payment_if_no_provider_payment_id(self, mock_refund_payment: Mock) -> None:
        RefundWhenReservationCancelled().on(
            ReservationCancelled(reservation_id="test_reservation_id", provider_payment_id=None)
        )

        mock_refund_payment.assert_not_called()
