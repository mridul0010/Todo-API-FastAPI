from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import TodoModel

app = FastAPI()

Base.metadata.create_all(bind=engine)


class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class TodoCreate(TodoBase):
    pass


class TodoUpdate(TodoBase):
    pass


class TodoResponse(TodoBase):
    id: int

    class Config:
        orm_mode = True


@app.get("/")
def home():
    return {"Message": "Welcome to the Todo Application"}


@app.get("/todos", response_model=List[TodoResponse])
def get_todos(db: Session = Depends(get_db)):
    return db.query(TodoModel).all()


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        ) 
    return todo


@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def add_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    new_todo = TodoModel(**todo.dict())
    db.add(new_todo)
    db.commit()                                            # To see the changes in original DB 
    db.refresh(new_todo)
    return new_todo


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    existing_todo = (db.query(TodoModel).filter(TodoModel.id == todo_id).first())
    if existing_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    for field, value in todo.dict().items():
        setattr(existing_todo, field, value)

    db.commit()
    db.refresh(existing_todo)
    return existing_todo


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    db.delete(todo)
    db.commit()
    return {"Message": "Todo deleted successfully"}
