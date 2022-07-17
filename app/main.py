from multiprocessing import current_process
from typing import Optional
import click
from fastapi import Body, FastAPI, Response, status, HTTPException
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time 


click.clear() # fix color codes on terminal

app = FastAPI()

# body validation (using pydantic)
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None


while True:
    try:
        conn = psycopg2.connect(
            host='localhost', 
            database='api-development-course', 
            user='postgres', 
            password='password123',
            cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successfull!")
        break
    except Exception as error:
        print("Connection to database failed")
        print("Error: ", error)
        time.sleep(2)


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
    cursor.execute(""" 
        SELECT * 
        FROM posts 
        """)
    posts = cursor.fetchall()
    return {"data": posts}

# everytime we create something we should return a 201 status code
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""
        INSERT INTO posts 
            (title, content, published) 
        VALUES
            (%s, %s, %s)
        RETURNING *
        """, (post.title, post.content, post.published)
        )
    new_post = cursor.fetchone()

    conn.commit()

    return {"data": new_post} 

# in order to get a specific post we should pass a path parameter
@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    cursor.execute("""
        SELECT *
        FROM posts
        WHERE id = %s
        """, (str(id))
        )
    post = cursor.fetchone()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} was not found")
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    cursor.execute("""
    DELETE FROM posts
    WHERE id = %s
    RETURNING *
    """, (str(id))
    )
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: Post):

    cursor.execute("""
    UPDATE posts SET 
        title = %s, 
        content = %s, 
        published = %s
    WHERE id = %s
    RETURNING *
    """, (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} does not exist")
    return {"data": updated_post}