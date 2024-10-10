import uuid
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class MovieShowtime:
    id: uuid.UUID
    show_datetime: datetime

    def is_future(self) -> bool:
        return self.show_datetime >= datetime.now(tz=timezone.utc)
