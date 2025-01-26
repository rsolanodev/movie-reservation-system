import logging
from typing import Any
from unittest.mock import Mock, create_autospec

import pytest

from app.payments.application.commands.refund_payment import RefundPayment, RefundPaymentParams
from app.payments.domain.repositories.reservation_repository import ReservationRepository
from app.payments.domain.reservation import Reservation
from app.shared.domain.clients.payment_client import PaymentClient
from app.shared.domain.exceptions import RefundError
from app.shared.domain.value_objects.id import Id
from app.shared.domain.value_objects.reservation_status import ReservationStatus


class TestRefundPayment:
    @pytest.fixture
    def mock_payment_client(self) -> Any:
        return create_autospec(spec=PaymentClient, spec_set=True, instance=True)

    @pytest.fixture
    def mock_reservation_repository(self) -> Any:
        return create_autospec(spec=ReservationRepository, spec_set=True, instance=True)

    @pytest.fixture
    def caplog(self, caplog: pytest.LogCaptureFixture) -> pytest.LogCaptureFixture:
        caplog.set_level(logging.INFO)
        return caplog

    def test_refunds_payment(
        self, mock_payment_client: Mock, mock_reservation_repository: Mock, caplog: pytest.LogCaptureFixture
    ) -> None:
        RefundPayment(payment_client=mock_payment_client, reservation_repository=mock_reservation_repository).execute(
            params=RefundPaymentParams(
                reservation_id="5661455d-de5a-47ba-b99f-f6d50fdfc00b", provider_payment_id="test_payment_id"
            )
        )

        mock_payment_client.refund_payment.assert_called_once_with(payment_id="test_payment_id")
        mock_reservation_repository.update.assert_called_once_with(
            Reservation(id=Id("5661455d-de5a-47ba-b99f-f6d50fdfc00b"), status=ReservationStatus.REFUNDED)
        )

        assert caplog.records[0].levelname == "INFO"
        assert caplog.records[0].message == "Refunding payment for reservation succeeded"
        assert caplog.records[0].reservation_id == "5661455d-de5a-47ba-b99f-f6d50fdfc00b"  # type: ignore
        assert caplog.records[0].payment_id == "test_payment_id"  # type: ignore

    def test_does_not_refund_payment_when_refund_fails(
        self, mock_payment_client: Mock, mock_reservation_repository: Mock, caplog: pytest.LogCaptureFixture
    ) -> None:
        mock_payment_client.refund_payment.side_effect = RefundError

        RefundPayment(payment_client=mock_payment_client, reservation_repository=mock_reservation_repository).execute(
            params=RefundPaymentParams(
                reservation_id="5661455d-de5a-47ba-b99f-f6d50fdfc00b", provider_payment_id="test_payment_id"
            )
        )

        mock_payment_client.refund_payment.assert_called_once_with(payment_id="test_payment_id")
        mock_reservation_repository.update.assert_not_called()

        assert caplog.records[0].levelname == "ERROR"
        assert caplog.records[0].message == "Refunding payment for reservation failed"
        assert caplog.records[0].reservation_id == "5661455d-de5a-47ba-b99f-f6d50fdfc00b"  # type: ignore
        assert caplog.records[0].payment_id == "test_payment_id"  # type: ignore
