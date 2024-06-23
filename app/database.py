from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# import psycopg2
# import time

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}'f'@{settings.database_hostname}:{settings.database_port}/fastapi-test'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# while True:
#     try:
#         conn = psycopg2.connect(
#             host='localhost',
#             dbname='Fastapi',
#             user='postgres',
#             password='Zaisan12',
#             cursor_factory=RealDictCursor
#         )
#         cursor = conn.cursor()
#         print("Database connection was successful!")
#         break
#     except Exception as error:
#         print("Connection failed")
#         print("Error:", error)
#         time.sleep(2)
