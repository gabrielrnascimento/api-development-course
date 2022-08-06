from fastapi.testclient import TestClient
import pytest

from app import schemas


def test_get_all_posts(authorized_client: TestClient, test_posts: list):
    res = authorized_client.get("/posts/")
    posts_map = map(lambda x: schemas.PostOut(**x), res.json())     # validade posts
    posts_list = list(posts_map)
    assert len(res.json()) == len(test_posts)
    assert res.status_code == 200


def test_unauthorized_user_get_all_posts(client: TestClient, test_posts: list):
    res = client.get("/posts/")
    assert res.status_code == 401


def test_unauthorized_user_get_one_posts(client: TestClient, test_posts: list):
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_get_one_post_not_exist(authorized_client: TestClient, test_posts: list):
    res = authorized_client.get("/posts/88888")
    assert res.status_code == 404


def test_get_one_post(authorized_client: TestClient, test_posts: list):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    post = schemas.PostOut(**res.json())
    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content
    assert post.Post.title == test_posts[0].title


@pytest.mark.parametrize("title, content, published", [
    ("awesome new title", "awesome new content", True),
    ("favorite pizza", "i love pepperoni", False),
    ("tallest skyscrapers", "wahoo", True),
])
def test_create_post(authorized_client: TestClient, test_user: dict, test_posts: list, title: str, content: str, published: bool):
    res = authorized_client.post("/posts/", json={
        "title": title,
        "content": content,
        "published": published
    })
    created_post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user['id']


def test_create_post_default_published_true(authorized_client: TestClient, test_user: dict, test_posts: list):
    res = authorized_client.post("/posts/", json={
        "title": "test title",
        "content": "test content"
    })
    created_post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == "test title"
    assert created_post.content == "test content"
    assert created_post.published == True
    assert created_post.owner_id == test_user['id']


def test_unauthorized_user_create_post(client: TestClient, test_user: dict, test_posts: list):
    res = client.post("/posts/", json={
        "title": "test title",
        "content": "test content"
    })
    assert res.status_code == 401


def test_unauthorized_user_delete_post(client: TestClient, test_user: dict, test_posts: list):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_delete_post_success(authorized_client: TestClient, test_user: dict, test_posts: list):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 204


def test_delete_post_non_exist(authorized_client: TestClient, test_user: dict, test_posts: list):
    res = authorized_client.delete("/posts/88888")
    assert res.status_code == 404


def test_delete_other_user_post(authorized_client: TestClient, test_user: dict, test_posts: list):
    res = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert res.status_code == 403


def test_update_post(authorized_client: TestClient, test_user: dict, test_posts: list):
    data = {
        "title": "updated title",
        "content": "updated contend",
        "id": test_posts[0].id
    }
    res = authorized_client.put(f"/posts/{data['id']}", json=data)
    updated_post = schemas.Post(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']


def test_update_other_user_post(authorized_client: TestClient, test_user: dict, test_user2: dict, test_posts: list):
    data = {
        "title": "updated title",
        "content": "updated contend",
        "id": test_posts[3].id
    }
    res = authorized_client.put(f"/posts/{data['id']}", json=data)
    assert res.status_code == 403


def test_unauthorized_user_update_post(client: TestClient, test_posts: list):
    res = client.put(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_update_post_non_exist(authorized_client: TestClient, test_user: dict, test_posts: list):
    data = {
        "title": "updated title",
        "content": "updated contend",
        "id": test_posts[3].id
    }
    res = authorized_client.put(f"posts/88888", json=data)
    assert res.status_code == 404