from collections.abc import Generator
from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.payments.application.commands.confirm_payment import ConfirmPaymentParams
from app.payments.domain.exceptions import InvalidSignature, ReservationNotFound
from app.shared.domain.payment_event import PaymentEvent
from app.shared.domain.value_objects.reservation_status import ReservationStatus
from app.shared.tests.infrastructure.builders.sqlmodel_reservation_builder import SqlModelReservationBuilder


class TestStripeWebhook:
    @pytest.fixture
    def mock_confirm_payment(self) -> Generator[Mock, None, None]:
        with patch("app.payments.infrastructure.api.webhooks.ConfirmPayment") as mock:
            yield mock

    @pytest.fixture
    def mock_stripe_client(self) -> Generator[Mock, None, None]:
        with patch("app.payments.infrastructure.api.webhooks.StripeClient") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_reservation_repository(self) -> Generator[Mock, None, None]:
        with patch("app.payments.infrastructure.api.webhooks.SqlModelReservationRepository") as mock:
            yield mock.return_value

    @pytest.fixture
    def mock_reservation_finder(self) -> Generator[Mock, None, None]:
        with patch("app.payments.infrastructure.api.webhooks.SqlModelReservationFinder") as mock:
            yield mock.return_value

    @pytest.mark.integration
    def test_integration(self, client: TestClient, session: Session, mock_stripe_client: Mock) -> None:
        reservation_model = (
            SqlModelReservationBuilder(session)
            .with_id(UUID("92ab35a6-ae79-4039-85b3-e8b2b8abb27d"))
            .with_provider_payment_id("pi_3MtwBwLkdIwHu7ix28a3tqPa")
            .pending()
            .build()
        )

        mock_stripe_client.verify_payment.return_value = PaymentEvent(
            type="payment_intent.succeeded", payment_intent_id="pi_3MtwBwLkdIwHu7ix28a3tqPa"
        )

        response = client.post(
            "api/v1/payments/stripe/",
            content=b'{"type": "payment_intent.succeeded"}',
            headers={"stripe-signature": "test_signature"},
        )

        assert response.status_code == 200
        assert reservation_model.status == ReservationStatus.CONFIRMED.value

    def test_returns_200_and_calls_confirm_payment(
        self,
        client: TestClient,
        mock_confirm_payment: Mock,
        mock_reservation_repository: Mock,
        mock_reservation_finder: Mock,
        mock_stripe_client: Mock,
    ) -> None:
        response = client.post(
            "api/v1/payments/stripe/",
            content=b'{"type": "payment_intent.succeeded"}',
            headers={"stripe-signature": "test_signature"},
        )

        mock_confirm_payment.assert_called_once_with(
            reservation_repository=mock_reservation_repository,
            reservation_finder=mock_reservation_finder,
            payment_client=mock_stripe_client,
        )
        mock_confirm_payment.return_value.execute.assert_called_once_with(
            params=ConfirmPaymentParams(
                payload=b'{"type": "payment_intent.succeeded"}',
                signature="test_signature",
            )
        )

        assert response.status_code == 200

    def test_returns_400_when_signature_is_invalid(self, client: TestClient, mock_confirm_payment: Mock) -> None:
        mock_confirm_payment.return_value.execute.side_effect = InvalidSignature

        response = client.post(
            "api/v1/payments/stripe/",
            content=b'{"type": "payment_intent.succeeded"}',
            headers={"stripe-signature": "invalid_signature"},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid signature"

    def test_returns_404_when_reservation_is_not_found(self, client: TestClient, mock_confirm_payment: Mock) -> None:
        mock_confirm_payment.return_value.execute.side_effect = ReservationNotFound

        response = client.post(
            "api/v1/payments/stripe/",
            content=b'{"type": "payment_intent.succeeded"}',
            headers={"stripe-signature": "test_signature"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Reservation not found"
