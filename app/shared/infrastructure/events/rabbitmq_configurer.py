from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel
from pika.exchange_type import ExchangeType

from app.settings import get_settings
from app.shared.domain.events.event_subscriber import EventSubscriber, TypeEvent

settings = get_settings()


class RabbitMQConfigurer:
    _exchange_name: str = "domain_events"

    def __init__(self) -> None:
        self._connection: BlockingConnection | None = None
        self._channel: BlockingChannel | None = None

    @property
    def exchange_name(self) -> str:
        return self._exchange_name

    def get_channel(self) -> BlockingChannel:
        self._connection = self._get_connection()

        if self._channel is None or self._channel.is_closed:
            self._channel = self._connection.channel()
            self._channel.exchange_declare(exchange=self._exchange_name, exchange_type=ExchangeType.topic, durable=True)
        return self._channel

    def add_subscriber(self, subscriber: type[EventSubscriber[TypeEvent]]) -> None:
        subscriber_instance = subscriber()
        topic = subscriber_instance.event_class.topic()
        queue_name = f"{topic}.{subscriber.action}"

        channel = self.get_channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(exchange=self._exchange_name, queue=queue_name, routing_key=topic)
        channel.basic_consume(queue=queue_name, on_message_callback=subscriber_instance.handle, auto_ack=True)

    def start(self) -> None:
        try:
            channel = self.get_channel()
            channel.start_consuming()
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        if self._channel and not self._channel.is_closed:
            self._channel.stop_consuming()
            self._channel.close()

        if self._connection and not self._connection.is_closed:
            self._connection.close()

    def _get_connection(self) -> BlockingConnection:
        if self._connection is None or self._connection.is_closed:
            self._connection = BlockingConnection(
                ConnectionParameters(
                    host=settings.RABBITMQ_HOST,
                    port=settings.RABBITMQ_PORT,
                    credentials=PlainCredentials(
                        username=settings.RABBITMQ_USER,
                        password=settings.RABBITMQ_PASSWORD,
                    ),
                    heartbeat=600,
                    blocked_connection_timeout=300,
                )
            )
        return self._connection
