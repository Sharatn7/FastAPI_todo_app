from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# postgres connection
SQLALCHEMY_DATABASE_URL = "postgresql://userdb:12345@localhost/postgres"
# SQLALCHEMY_DATABASE_URL = os.getenv("DB_URL")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
