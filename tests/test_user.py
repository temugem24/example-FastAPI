from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from sqlalchemy.ext.declarative import declarative_base
from app.database import get_db, Base
#mock dependancy 
from app import main
from fastapi.testclient import TestClient
from app.schemas import UserOut


SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@64.23.128.76:{settings.database_port}/{settings.database_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

main.app.dependency_overrides[get_db] = override_get_db
   

client = TestClient(main.app)


def test_root():
    res = client.get("/")
    assert res.json() == {"message": "Welcome to the home page"}
    assert res.status_code == 200 

def test_create_user():
    res = client.post("/users/", json = {"email": "tee@gmail.com", "password": "password123"})
    
    new_user= UserOut(**res.json())
    assert new_user.email == "tee@gmail.com"
    assert res.status_code == 201
