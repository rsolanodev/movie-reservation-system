from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from app.payments.application.commands.confirm_payment import ConfirmPaymentParams
from app.payments.domain.exceptions import InvalidSignature


class TestStripeWebhook:
    @pytest.fixture
    def mock_confirm_payment(self) -> Generator[Mock, None, None]:
        with patch("app.payments.infrastructure.api.webhooks.ConfirmPayment") as mock:
            yield mock

    def test_returns_200_and_calls_confirm_payment(self, client: TestClient, mock_confirm_payment: Mock) -> None:
        response = client.post(
            "api/v1/payments/stripe/",
            content=b'{"type": "payment_intent.succeeded"}',
            headers={"stripe-signature": "test_signature"},
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
