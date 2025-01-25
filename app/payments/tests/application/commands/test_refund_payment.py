import logging
from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.payments.application.commands.refund_payment import RefundPayment, RefundPaymentParams
from app.shared.domain.clients.payment_client import PaymentClient
from app.shared.domain.exceptions import RefundError


class TestRefundPayment:
    @pytest.fixture
    def mock_payment_client(self) -> Any:
        return create_autospec(spec=PaymentClient, spec_set=True, instance=True)

    @pytest.fixture
    def caplog(self, caplog: pytest.LogCaptureFixture) -> pytest.LogCaptureFixture:
        caplog.set_level(logging.INFO)
        return caplog

    def test_refunds_payment(self, mock_payment_client: Mock, caplog: pytest.LogCaptureFixture) -> None:
        RefundPayment(payment_client=mock_payment_client).execute(
            RefundPaymentParams(reservation_id="test_reservation_id", provider_payment_id="test_payment_id")
        )

        mock_payment_client.refund_payment.assert_called_once_with(payment_id="test_payment_id")

        assert caplog.records[0].levelname == "INFO"
        assert caplog.records[0].message == "Refunding payment for reservation succeeded"
        assert caplog.records[0].reservation_id == "test_reservation_id"  # type: ignore
        assert caplog.records[0].payment_id == "test_payment_id"  # type: ignore

    def test_does_not_refund_payment_when_refund_fails(
        self, mock_payment_client: Mock, caplog: pytest.LogCaptureFixture
    ) -> None:
        mock_payment_client.refund_payment.side_effect = RefundError

        RefundPayment(payment_client=mock_payment_client).execute(
            RefundPaymentParams(reservation_id="test_reservation_id", provider_payment_id="test_payment_id")
        )

        mock_payment_client.refund_payment.assert_called_once_with(payment_id="test_payment_id")

        assert caplog.records[0].levelname == "ERROR"
        assert caplog.records[0].message == "Refunding payment for reservation failed"
        assert caplog.records[0].reservation_id == "test_reservation_id"  # type: ignore
        assert caplog.records[0].payment_id == "test_payment_id"  # type: ignore
