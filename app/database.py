from collections.abc import Generator
from contextlib import contextmanager

from sqlmodel import Session, create_engine

from app.settings import get_settings

settings = get_settings()

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


@contextmanager
def get_session() -> Generator[Session, None, None]:
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
