from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.utils.env import env_get

DB_URL = env_get("DB_URL")
engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
