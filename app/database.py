from collections.abc import Generator
from contextlib import contextmanager

from sqlmodel import Session, create_engine

from app.settings import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
