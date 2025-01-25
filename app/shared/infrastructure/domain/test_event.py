from dataclasses import dataclass
from typing import Any, Self

import pytest

from app.shared.domain.events.event import Event


@dataclass(frozen=True)
class EventTested(Event):
    event_id: int
    reason: str

    @classmethod
    def topic(cls) -> str:
        return "event.tested"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(event_id=data["event_id"], reason=data["reason"])


class TestEvent:
    @pytest.fixture
    def event(self) -> Event:
        return EventTested(event_id=123, reason="testing")

    def test_topic(self, event: Event) -> None:
        assert event.topic() == "event.tested"

    def test_from_dict(self) -> None:
        event = EventTested.from_dict({"event_id": 123, "reason": "testing"})

        assert event.event_id == 123
        assert event.reason == "testing"

    def test_to_dict(self, event: Event) -> None:
        assert event.to_dict() == {"event_id": 123, "reason": "testing"}
