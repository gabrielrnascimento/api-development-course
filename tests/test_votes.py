from hashlib import new
from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from app import models



@pytest.fixture
def test_vote(test_user: dict, test_posts: list, session: Session):
    new_vote = models.Vote(post_id=test_posts[3].id, user_id=test_user['id'])
    session.add(new_vote)
    session.commit()


def test_vote_on_post(authorized_client: TestClient, test_posts: list):
    res = authorized_client.post("/vote/", json={
        "post_id": test_posts[3].id,
        "dir": 1
        })
    assert res.status_code == 201


def test_vote_twice_post(authorized_client: TestClient, test_posts: list, test_vote: None):
    res = authorized_client.post("/vote/", json={
        "post_id": test_posts[3].id,
        "dir": 1
    })
    assert res.status_code == 409


def test_delete_vote(authorized_client: TestClient, test_posts: list, test_vote: None):
    res = authorized_client.post("/vote/", json={
        "post_id": test_posts[3].id,
        "dir": 0
    })
    assert res.status_code == 201


def test_delete_vote_non_exist(authorized_client: TestClient, test_posts: list):
    res = authorized_client.post("/vote/", json={
        "post_id": test_posts[3].id,
        "dir": 0
    })
    assert res.status_code == 404


def test_vote_post_non_exist(authorized_client: TestClient, test_posts: list):
    res = authorized_client.post("/vote/", json={
        "post_id": 88888,
        "dir": 1
    })
    assert res.status_code == 404


def test_vote_unauthorized_user(client: TestClient, test_posts: list):
    res = client.post("/vote/", json={
        "post_id": test_posts[3].id,
        "dir": 1
    })
    assert res.status_code == 401
