from typing import Any
from unittest.mock import Mock, create_autospec

import pytest
from pika.adapters.blocking_connection import BlockingChannel

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
