from fastapi import APIRouter, HTTPException, Request, status

from app.payments.application.commands.confirm_payment import ConfirmPayment, ConfirmPaymentParams
from app.payments.domain.exceptions import InvalidSignature

router = APIRouter()


@router.post("/stripe/", status_code=status.HTTP_200_OK)
async def stripe(request: Request) -> None:
    try:
        payload = await request.body()
        signature = request.headers["stripe-signature"]

        ConfirmPayment().execute(params=ConfirmPaymentParams(payload=payload, signature=signature))
    except InvalidSignature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")
