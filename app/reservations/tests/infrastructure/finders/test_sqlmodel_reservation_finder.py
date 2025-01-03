from uuid import UUID

import pytest
from sqlmodel import Session

from app.reservations.domain.reservation import Reservation
from app.reservations.infrastructure.finders.sqlmodel_reservation_finder import SqlModelReservationFinder
from app.reservations.tests.builders.sqlmodel_reservation_builder_test import SqlModelReservationBuilderTest
from app.shared.domain.value_objects.id import Id


class TestSqlModelReservationFinder:
    @pytest.mark.parametrize("has_paid", [False, True])
    def test_find_reservation(self, session: Session, has_paid: bool) -> None:
        reservation_model = (
            SqlModelReservationBuilderTest(session)
            .with_id(UUID("92ab35a6-ae79-4039-85b3-e8b2b8abb27d"))
            .with_user_id(UUID("47d653d5-971e-42c3-86ab-2c7f40ef783a"))
            .with_showtime_id(UUID("ffa502e6-8869-490c-8799-5bea26c7146d"))
            .with_has_paid(has_paid)
            .build()
        )

        reservation = SqlModelReservationFinder(session).find_reservation(
            reservation_id=Id.from_uuid(reservation_model.id),
        )

        assert reservation == Reservation(
            id=Id("92ab35a6-ae79-4039-85b3-e8b2b8abb27d"),
            user_id=Id("47d653d5-971e-42c3-86ab-2c7f40ef783a"),
            showtime_id=Id("ffa502e6-8869-490c-8799-5bea26c7146d"),
            has_paid=has_paid,
        )
