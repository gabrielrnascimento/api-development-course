from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import pytest

from app.main import app
from app import schemas
from app.config import settings
from app.database import get_db, Base
from app.oauth2 import create_access_token
from app import models


SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#? getting access to the database object
@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)     # after our code runs, drop my tables
    Base.metadata.create_all(bind=engine)   # before our code runs, create my tables
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

#? getting access to the client object
@pytest.fixture()
def client(session):
    #? run our code before we run our test
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    #? run our code after our test finishes


@pytest.fixture
def test_user(client: TestClient) -> dict:
    user_data = {
        "email": "test_user@gmail.com",
        "password": "testpassword123"
    }
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def test_user2(client: TestClient) -> dict:
    user_data = {
        "email": "test_user2@gmail.com",
        "password": "testpassword123"
    }
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def token(test_user: dict):
    return create_access_token({"user_id": test_user['id']})

@pytest.fixture
def authorized_client(client: TestClient, token: str):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture
def test_posts(test_user: dict, test_user2: dict, session: Session) -> list:
    posts_data = [{
            "title": "first title",
            "content": "first content",
            "owner_id": test_user['id']}, 
        {
            "title": "2nd title",
            "content": "2nd content",
            "owner_id": test_user['id']
        }, {
            "title": "3rd title",
            "content": "3rd content",
            "owner_id": test_user['id']
        }, {
            "title": "4th title",
            "content": "4th content",
            "owner_id": test_user2['id']
        }]

    post_map = map(lambda x: models.Post(**x), posts_data)
    posts = list(post_map)
    session.add_all(posts)
    session.commit()
    posts = session.query(models.Post).all()
    return posts




