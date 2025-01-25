import json

from app.shared.domain.events.event import Event
from app.shared.domain.events.event_bus import EventBus
from app.shared.infrastructure.events.rabbitmq_configurer import RabbitMQConfigurer


class RabbitMQEventBus(EventBus):
    def __init__(self, configurer: RabbitMQConfigurer) -> None:
        self._configurer = configurer
        self._channel = self._configurer.get_channel()

    def publish(self, events: list[Event]) -> None:
        for event in events:
            self._channel.basic_publish(
                exchange=self._configurer.exchange_name,
                routing_key=event.topic(),
                body=json.dumps(event.to_dict()),
            )
