from typing import Protocol

from app.shared.domain.events.event import Event


class EventBus(Protocol):
    def publish(self, events: list[Event]) -> None: ...
