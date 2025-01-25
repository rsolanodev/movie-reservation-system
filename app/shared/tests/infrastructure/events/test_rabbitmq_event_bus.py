import json
from typing import Any
from unittest.mock import Mock, create_autospec

import pytest
from pika.adapters.blocking_connection import BlockingChannel

from app.reservations.domain.events import ReservationCancelled
from app.shared.infrastructure.events.rabbitmq_configurer import RabbitMQConfigurer
from app.shared.infrastructure.events.rabbitmq_event_bus import RabbitMQEventBus


class TestRabbitMQEventBus:
    @pytest.fixture
    def mock_configurer(self) -> Any:
        return create_autospec(RabbitMQConfigurer, spec_set=True, instance=True)

    @pytest.fixture
    def mock_channel(self, mock_configurer: Any) -> Any:
        mock_channel = create_autospec(BlockingChannel, spec_set=True, instance=True)
        mock_configurer.get_channel.return_value = mock_channel
        return mock_channel

    def test_does_not_publish_if_no_events(self, mock_configurer: Mock, mock_channel: Mock) -> None:
        RabbitMQEventBus(mock_configurer).publish([])

        mock_channel.basic_publish.assert_not_called()

    def test_publishes_reservation_cancelled_event(self, mock_configurer: Mock, mock_channel: Mock) -> None:
        event = ReservationCancelled(
            reservation_id="a41707bd-ae9c-43b8-bba5-8c4844e73e77", provider_payment_id="pi_3MtwBwLkdIwHu7ix28a3tqPa"
        )

        RabbitMQEventBus(mock_configurer).publish([event])

        mock_channel.basic_publish.assert_called_once_with(
            exchange=mock_configurer.exchange_name,
            routing_key="reservation.cancelled",
            body=json.dumps(
                {
                    "reservation_id": "a41707bd-ae9c-43b8-bba5-8c4844e73e77",
                    "provider_payment_id": "pi_3MtwBwLkdIwHu7ix28a3tqPa",
                }
            ),
        )
