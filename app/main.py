from multiprocessing import current_process
from typing import Optional
import click
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time 
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db


models.Base.metadata.create_all(bind=engine)

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


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):

    posts = db.query(models.Post).all()
    return {"data": posts}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    
    # ? (old) regular SQL method for database query
    # cursor.execute(""" SELECT * FROM posts """)
    # posts = cursor.fetchall()

    # ? using ORM for database query
    posts = db.query(models.Post).all()
    return {"data": posts}

# everytime we create something we should return a 201 status code
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    
    # ? (old) regular SQL method for database query
    # cursor.execute("""
    #     INSERT INTO posts (title, content, published) 
    #     VALUES (%s, %s, %s)
    #     RETURNING *
    #     """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    # ? using ORM for database query
    # new_post = models.Post(
    #     title=post.title, content=post.content, published=post.published)
    new_post = models.Post(**post.dict()) # ! unpacking dict (more efficient than above method)
    
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {"data": new_post} 

# in order to get a specific post we should pass a path parameter
@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    # ? (old) regular SQL method for database query
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id)))
    # post = cursor.fetchone()
    
    # ? using ORM for database query
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} was not found")
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # ? (old) regular SQL method for database query
    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    # ? using ORM for database query
    post = db.query(models.Post).filter(models.Post.id == id)


    if post.first() == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} does not exist")
            
    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, updated_post: Post, db: Session = Depends(get_db)):

    # ? (old) regular SQL method for database query
    # cursor.execute(""" UPDATE posts 
    # SET title = %s, content = %s, published = %s 
    # WHERE id = %s
    # RETURNING * """, (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    # ? using ORM for database query
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} does not exist")

    # post_query.update({
    #     'title': 'hey this is my updated title',
    #     'content': 'this is my updated content'}, synchronize_session=False) # ! not optimal solution

    post_query.update(updated_post.dict(), synchronize_session=False) # ! best solution
    
    db.commit()

    return {"data": post_query.first()}