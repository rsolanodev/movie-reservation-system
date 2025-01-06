from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Connection, Engine, create_engine
from sqlalchemy_utils import create_database, database_exists
from sqlmodel import Session, SQLModel

from app.api.deps import get_fastapi_session
from app.auth.domain.token import Token
from app.main import app
from app.settings import Settings, get_settings
from app.shared.domain.value_objects.id import Id
from app.shared.tests.factories.user_factory_test import UserFactoryTest
from app.users.infrastructure.models import UserModel


@pytest.fixture
def settings() -> Settings:
    return get_settings()


@pytest.fixture
def engine() -> Engine:
    return create_engine("sqlite://", connect_args={"check_same_thread": False})


@pytest.fixture
def setup_database(engine: Engine) -> Generator[None, None, None]:
    if not database_exists(engine.url):
        create_database(engine.url)

    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def connection(
    engine: Engine,
    setup_database: None,  # noqa: ARG001
) -> Generator[Connection, None, None]:
    conn = engine.connect()
    yield conn
    conn.close()


@pytest.fixture
def session(connection: Connection) -> Generator[Session, None, None]:
    with Session(bind=connection) as session:
        try:
            yield session
            session.rollback()
        finally:
            session.close()


@pytest.fixture
def client(session: Session) -> Generator[TestClient, None, None]:
    def get_override_session() -> Session:
        return session

    app.dependency_overrides[get_fastapi_session] = get_override_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def user(session: Session) -> UserModel:
    user = UserFactoryTest().create()
    user_model = UserModel.from_domain(user)
    session.add(user_model)
    session.commit()
    return user_model


@pytest.fixture
def superuser(session: Session) -> UserModel:
    user = UserFactoryTest().create(is_superuser=True)
    user_model = UserModel.from_domain(user)
    session.add(user_model)
    session.commit()
    return user_model


@pytest.fixture
def user_token_headers(user: UserModel, settings: Settings) -> dict[str, str]:
    token = Token.create(
        user_id=Id.from_uuid(user.id),
        secret_key=settings.SECRET_KEY,
        expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return {"Authorization": f"Bearer {token.access_token}"}


@pytest.fixture
def superuser_token_headers(superuser: UserModel, settings: Settings) -> dict[str, str]:
    token = Token.create(
        user_id=Id.from_uuid(superuser.id),
        secret_key=settings.SECRET_KEY,
        expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return {"Authorization": f"Bearer {token.access_token}"}
