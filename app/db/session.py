from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# This network has repeatedly shown transient stalls (pip, DBeaver driver
# downloads, and occasionally the DB connection itself just going quiet
# mid-query with Postgres idly waiting on the client). Without a statement
# timeout, a stall like that hangs the request - or the whole app, if it
# happens during startup - forever. connect_timeout covers the initial TCP
# handshake; statement_timeout (server-side, milliseconds) covers a query
# that starts but then stalls.
engine = create_engine(
    settings.database_url,
    connect_args={
        "connect_timeout": 10,
        "options": "-c statement_timeout=15000",
    },
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
