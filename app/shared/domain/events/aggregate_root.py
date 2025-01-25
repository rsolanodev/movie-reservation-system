from dataclasses import dataclass, field

from app.shared.domain.events.event import Event


@dataclass
class AggregateRoot:
    _events: list[Event] = field(default_factory=list, init=False)

    def record(self, event: Event) -> None:
        self._events.append(event)

    def collect_events(self) -> list[Event]:
        events, self._events = self._events, []
        return events
