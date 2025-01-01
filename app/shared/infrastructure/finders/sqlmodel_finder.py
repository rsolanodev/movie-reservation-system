from sqlmodel import Session


class SqlModelFinder:
    def __init__(self, session: Session) -> None:
        self._session = session
