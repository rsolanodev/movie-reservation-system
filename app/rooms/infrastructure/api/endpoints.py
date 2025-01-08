from fastapi import APIRouter, Depends, status

from app.api.deps import SessionDep, get_current_active_superuser
from app.rooms.application.commands.create_room import CreateRoom, CreateRoomParams
from app.rooms.infrastructure.api.payloads import CreateRoomPayload
from app.rooms.infrastructure.repositories.sqlmodel_room_repository import SqlModelRoomRepository

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_active_superuser)])
def create_room(session: SessionDep, request_body: CreateRoomPayload) -> None:
    CreateRoom(repository=SqlModelRoomRepository(session=session)).execute(
        params=CreateRoomParams(name=request_body.name, seat_configuration=request_body.seat_configuration)
    )
