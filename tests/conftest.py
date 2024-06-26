from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import get_db
from app import main
from fastapi.testclient import TestClient
from app.oauth2 import create_access_token
from app import models
import pytest
#mock dependancy 

SQLALCHEMY_TESTING_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}"f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}-test"
engine = create_engine(SQLALCHEMY_TESTING_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

@pytest.fixture
def session():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():

        try:
            yield session
        finally:
            session.close()
    main.app.dependency_overrides[get_db] = override_get_db
    yield TestClient(main.app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "orange@gmail.com",
                  "password": "password"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def test_user2(client):
    user_data = {"email": "orange123@gmail.com",
                  "password": "password123"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [
        {
            "title": "first title",
            "content": "first content",
            "owner_id": test_user['id']
        },
        {
            "title": "2nd title",
            "content": "2nd content",
            "owner_id": test_user['id']
        },
        {
            "title": "3rd title",
            "content": "3rd content",
            "owner_id": test_user['id']
        },
        {
            "title": "3rd title",
            "content": "3rd content",
            "owner_id": test_user2['id']
        }
    ]

    def create_post_model(post):
        return models.Post(**post)
    
    post_map = map(create_post_model, posts_data)
    post = list(post_map)

    session.add_all(post)

    # session.add_all([models.Post(title="first title", content="first content", owner_id = test_user['id']),
    #                  models.Post(title="2nd title", content="2nd content", owner_id = test_user['id']),
    #                  models.Post(title="3rd title", content="3rd content", owner_id = test_user['id'])])
    
    session.commit()

    posts = session.query(models.Post).all()

    return posts
    