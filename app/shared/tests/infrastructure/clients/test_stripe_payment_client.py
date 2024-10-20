from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest

from app.shared.infrastructure.clients.stripe_payment_client import StripePaymentClient


class TestStripePaymentClient:
    @pytest.fixture(autouse=True)
    def mock_stripe_settings(self) -> Generator[None, None, None]:
        with patch("app.shared.infrastructure.clients.stripe_payment_client.settings") as settings:
            settings.STRIPE_API_KEY = "sk_test_apikey"
            yield

    @pytest.fixture
    def mock_stripe_client(self) -> Generator[Mock, None, None]:
        with patch("app.shared.infrastructure.clients.stripe_payment_client.StripeClient") as mock:
            yield mock

    @pytest.fixture
    def mock_stripe_session(self) -> Generator[Mock, None, None]:
        with patch("app.shared.infrastructure.clients.stripe_payment_client.StripeClient.checkout.Session") as mock:
            yield mock

    def test_create_payment(self, mock_stripe_client: Mock, mock_stripe_session: Mock) -> None:
        mock_stripe_session.create.return_value = "session_id"

        StripePaymentClient().create_checkout_session()

        mock_stripe_client.assert_called_once_with(api_key="sk_test_apikey")
