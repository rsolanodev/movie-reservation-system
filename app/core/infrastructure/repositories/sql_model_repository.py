from sqlmodel import Session


class SqlModelRepository:
    def __init__(self, session: Session) -> None:
        self._session = session
