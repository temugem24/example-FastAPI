from sqlalchemy.orm import Session
from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from typing import List
from ..database import get_db
from typing import Optional
from sqlalchemy import func

router = APIRouter(
    prefix = "/posts",
    tags = ["posts"]
)

@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), limit: int = 25, skip: int = 0, search: Optional[str] = ""):

    posts = db.query(
        models.Post, func.count(models.Vote.post_id).label("votes")).outerjoin(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).filter(
        models.Post.title.contains(search)).group_by(
        models.Post.id).limit(limit).offset(skip).all()
    
    posts_with_votes = [
        schemas.PostOut(Post=post, Votes=votes) for post, votes in posts
    ]

    return posts_with_votes


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db)):

    result = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).outerjoin(
        models.Vote, models.Vote.post_id == models.Post.id).filter(models.Post.id == id).group_by(models.Post.id).first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post id: {id} was not found")
    
    post, votes = result
    post_with_votes = schemas.PostOut(Post=post, Votes=votes)

    return post_with_votes


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(owner_id = current_user.id, **post.model_dump()) 
    # "model_dump" is new version of "dict" from BaseModel
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    
    if post.owner_id != current_user.id:
        raise  HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail = "Not authorized to perform requeseted action")        

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", 
    #                (post.title, post.content, post.published, id))
    # updated_post = cursor.fetchone()
    # conn.commit() 
    post_query = db.query(models.Post).filter(models.Post.id == id)
    existing_post = post_query.first()

    if existing_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} does not exist")
    
    if existing_post.owner_id != current_user.id:
        raise  HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail = "Not authorized to perform requeseted action") 

    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()