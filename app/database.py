from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import redis

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # For development. Use PostgreSQL for production.

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def create_redis():
  return redis.ConnectionPool(
    host='localhost', 
    port=6379, 
    db=0, 
    decode_responses=True
  )

pool = create_redis()