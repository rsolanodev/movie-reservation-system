from dataclasses import dataclass

from app.shared.domain.value_objects.date_time import DateTime
from app.shared.domain.value_objects.id import Id


@dataclass
class MovieShowtime:
    id: Id
    show_datetime: DateTime

    def is_future(self) -> bool:
        return self.show_datetime >= DateTime.now()
