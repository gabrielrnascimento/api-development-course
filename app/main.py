from logging import raiseExceptions
from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange

app = FastAPI()

# body validation (using pydantic)
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

# dummy database for testing CRUD operations
my_posts = [
    {"title": "title of post 1", "content": "content of post 1", "id": 1}, 
    {"title": "favorite foods", "content": "I like pizza", "id": 2}
    ]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/posts")
def get_posts():
    return {"data": my_posts}

# ! everytime we create something we should return a 201 status code
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.dict()
    post_dict["id"] = randrange(0, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict} 

# in order to get a specific post we should pass a path parameter
@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} was not found")
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # deleting post
    # find the index in the array that has the required ID
    #  my_posts.pop(index)
    index = find_index_post(id)
    if index == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} does not exist")
    my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)
    if index == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} does not exist")
    post_dict = post.dict()
    post_dict["id"] = id
    my_posts[index] = post_dict
    return {"data": post_dict}