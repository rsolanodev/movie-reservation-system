from sqlmodel import create_engine

from app.settings import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
