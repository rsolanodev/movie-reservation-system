from dataclasses import dataclass
from datetime import datetime, timezone

from app.shared.domain.value_objects.id import Id


@dataclass
class MovieShowtime:
    id: Id
    show_datetime: datetime

    def is_future(self) -> bool:
        return self.show_datetime >= datetime.now(tz=timezone.utc)
