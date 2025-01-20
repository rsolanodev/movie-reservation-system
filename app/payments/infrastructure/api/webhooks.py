from fastapi import APIRouter, HTTPException, Request, status

from app.api.deps import SessionDep
from app.payments.application.commands.confirm_payment import ConfirmPayment, ConfirmPaymentParams
from app.payments.domain.exceptions import InvalidSignature
from app.payments.infrastructure.finders.sqlmodel_reservation_finder import SqlModelReservationFinder
from app.payments.infrastructure.repositories.sqlmodel_reservation_repository import SqlModelReservationRepository
from app.shared.infrastructure.clients.stripe_client import StripeClient

router = APIRouter()


@router.post("/stripe/", status_code=status.HTTP_200_OK)
async def stripe(request: Request, session: SessionDep) -> None:
    try:
        payload = await request.body()
        signature = request.headers["stripe-signature"]

        ConfirmPayment(
            reservation_finder=SqlModelReservationFinder(session=session),
            reservation_repository=SqlModelReservationRepository(session=session),
            payment_client=StripeClient(),
        ).execute(params=ConfirmPaymentParams(payload=payload, signature=signature))
    except InvalidSignature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
