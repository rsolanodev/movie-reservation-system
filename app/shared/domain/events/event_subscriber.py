from abc import ABC, abstractmethod
from json import loads
from typing import Generic, TypeVar

from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from app.shared.domain.events.event import Event

TypeEvent = TypeVar("TypeEvent", bound="Event")


class EventSubscriber(Generic[TypeEvent], ABC):
    action: str

    @property
    def event_class(self) -> type[TypeEvent]:
        return self.__class__.__orig_bases__[0].__args__[0]  # type: ignore

    def handle(self, channel: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes) -> None:
        self.on(event=self.event_class.from_dict(data=loads(body.decode())))

    @abstractmethod
    def on(self, event: TypeEvent) -> None:
        raise NotImplementedError
