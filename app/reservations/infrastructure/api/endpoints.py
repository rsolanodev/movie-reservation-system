from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, SessionDep
from app.reservations.application.commands.cancel_reservation import CancelReservation, CancelReservationParams
from app.reservations.application.commands.create_reservation import CreateReservation, CreateReservationParams
from app.reservations.application.queries.find_reservations import FindReservations
from app.reservations.domain.exceptions import (
    CancellationNotAllowed,
    ReservationDoesNotExist,
    SeatsNotAvailable,
    UnauthorizedCancellation,
)
from app.reservations.infrastructure.api.payloads import CreateReservationPayload
from app.reservations.infrastructure.api.responses import PaymentIntentResponse, ReservationResponse
from app.reservations.infrastructure.finders.sqlmodel_reservation_finder import SqlModelReservationFinder
from app.reservations.infrastructure.finders.sqlmodel_seat_finder import SqlModelSeatFinder
from app.reservations.infrastructure.repositories.sqlmodel_reservation_repository import SqlModelReservationRepository
from app.shared.domain.value_objects.id import Id
from app.shared.infrastructure.clients.stripe_client import StripeClient

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_reservation(
    session: SessionDep, request_body: CreateReservationPayload, current_user: CurrentUser
) -> PaymentIntentResponse:
    try:
        payment_intent = CreateReservation(
            reservation_repository=SqlModelReservationRepository(session=session),
            seat_finder=SqlModelSeatFinder(session=session),
            payment_client=StripeClient(),
        ).execute(
            params=CreateReservationParams(
                showtime_id=Id(request_body.showtime_id),
                seat_ids=[Id(seat_id) for seat_id in request_body.seat_ids],
                user_id=Id.from_uuid(current_user.id),
            )
        )
    except SeatsNotAvailable:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seats not available")
    return PaymentIntentResponse.from_domain(payment_intent)


@router.get("/", response_model=list[ReservationResponse], status_code=status.HTTP_200_OK)
def list_reservations(session: SessionDep, current_user: CurrentUser) -> list[ReservationResponse]:
    movie_reservations = FindReservations(finder=SqlModelReservationFinder(session=session)).execute(
        user_id=Id.from_uuid(current_user.id)
    )
    return ReservationResponse.from_domain_list(movie_reservations)


@router.delete("/{reservation_id}/", status_code=status.HTTP_204_NO_CONTENT)
def cancel_reservation(session: SessionDep, reservation_id: str, current_user: CurrentUser) -> None:
    try:
        CancelReservation(
            finder=SqlModelReservationFinder(session=session),
            repository=SqlModelReservationRepository(session=session),
        ).execute(
            params=CancelReservationParams(
                reservation_id=Id(reservation_id),
                user_id=Id.from_uuid(current_user.id),
            )
        )
    except ReservationDoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found")
    except UnauthorizedCancellation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unauthorized to cancel this reservation")
    except CancellationNotAllowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Showtime has started")
