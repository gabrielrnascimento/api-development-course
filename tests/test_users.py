from jose import jwt
from fastapi.testclient import TestClient
import pytest

from app import schemas
from app.config import settings




# def test_root(client: TestClient):
#     res = client.get("/")
#     assert res.json().get('message') == "Hello World"
#     assert res.status_code == 200

def test_create_user(client: TestClient):
    res = client.post("/users/", json={
        "email": "hello123@gmail.com", 
        "password": "password123"})

    new_user = schemas.UserOut(**res.json())
    assert new_user.email == "hello123@gmail.com"
    assert res.status_code == 201

def test_login_user(client: TestClient, test_user: dict):
    res = client.post("/login", data={
        "username": test_user['email'], 
        "password": test_user['password']})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(
        login_res.access_token, 
        settings.secret_key, 
        algorithms=[settings.algorithm])
    id: str = payload.get("user_id")

    assert id == test_user['id']
    assert login_res.token_type == "bearer"
    assert res.status_code == 200

@pytest.mark.parametrize("email, password, status_code",[
    ('wrongemail@gmail.com', 'password123', 403),
    ('gabriel@gmail.com', 'wrongpassword', 403),
    ('wrongemail@gmail.com', 'wrongpassword', 403),
    (None, 'password123', 422),
    ('gabriel@gmail.com', None, 422)
])
def test_incorrect_login(client: TestClient, test_user: dict, email: str, password: str, status_code: int):
    res = client.post("/login", data={
        "username": email,
        "password": password})
    
    assert res.status_code == status_code
    # assert res.json().get('detail') == "Invalid credentials"
    