from click import get_current_context
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, oauth2
from ..database import get_db



router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.get("/", response_model=List[schemas.Post])
def get_posts(
    db: Session = Depends(get_db), 
    current_user: dict = Depends(oauth2.get_current_user),
    limit: int = 10, skip: int = 0, search: Optional[str] = ""): # ! query parameters
    
    # ? (old) regular SQL method for database query
    # cursor.execute(""" SELECT * FROM posts """)
    # posts = cursor.fetchall()

    # ? using ORM for database query
    
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all() # ! retrieve only posts from the current user
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return posts

# everytime we create something we should return a 201 status code
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    
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

    new_post = models.Post(owner_id=current_user.id, **post.dict()) # ! unpacking dict (more efficient than above method)
        
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

# in order to get a specific post we should pass a path parameter
@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    # ? (old) regular SQL method for database query
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id)))
    # post = cursor.fetchone()
    
    # ? using ORM for database query
    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} was not found")

    # if post.owner_id != current_user.id: # ! retrieve only posts from the current user
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

        
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):
    # ? (old) regular SQL method for database query
    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    # ? using ORM for database query
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"post with id: {id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
            
    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: dict = Depends(oauth2.get_current_user)):

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

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")


    # post_query.update({
    #     'title': 'hey this is my updated title',
    #     'content': 'this is my updated content'}, synchronize_session=False) # ! not optimal solution

    post_query.update(updated_post.dict(), synchronize_session=False) # ! best solution
    
    db.commit()

    return post_query.first()