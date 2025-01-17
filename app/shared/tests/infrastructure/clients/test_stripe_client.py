from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest

from app.settings import Settings
from app.shared.domain.payment_intent import PaymentIntent
from app.shared.infrastructure.clients.stripe_client import StripeClient


class TestStripeClient:
    @pytest.fixture
    def mock_stripe(self) -> Generator[Mock, None, None]:
        with patch("app.shared.infrastructure.clients.stripe_client.stripe") as mock:
            yield mock

    @pytest.fixture(autouse=True)
    def override_settings(self) -> Generator[None, None, None]:
        with patch(
            "app.shared.infrastructure.clients.stripe_client.settings",
            Settings(STRIPE_API_KEY="test_api_key", STRIPE_DEFAULT_CURRENCY="eur"),
        ):
            yield

    def test_creates_payment_intent(self, mock_stripe: Mock) -> None:
        mock_stripe.PaymentIntent.create.return_value = Mock(
            client_secret="test_client_secret", id="test_provider_payment_id"
        )

        payment_intent = StripeClient().create_payment_intent(amount=10.0)

        mock_stripe.PaymentIntent.create.assert_called_once_with(
            amount=1000, currency="eur", automatic_payment_methods={"enabled": True}
        )

        assert payment_intent == PaymentIntent(
            client_secret="test_client_secret", provider_payment_id="test_provider_payment_id", amount=10.0
        )
