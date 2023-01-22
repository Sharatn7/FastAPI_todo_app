
# importing necessary modules
from fastapi import Depends, APIRouter, Request, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from .auth import get_current_user
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from typing import Optional
import models
from ast import For
import sys
sys.path.append("..")

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Todo(BaseModel):
    title: str
    description: Optional[str]


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todos = db.query(models.Todos).filter(
        models.Todos.owner_id == user.get("id")).all()
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos, "user": user})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})

''' creating a new todo and adding it to the database.'''
@router.post("/add-todo", response_class=HTMLResponse)
async def create_todo(request: Request, title: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo_model = models.Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

''' fetching a todo from the database and passing it to the view-todo.html template.'''
@router.get("/get-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    return templates.TemplateResponse("view-todo.html", {"request": request, "todo": todo, "user": user})


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo = db.query(models.Todos).filter(models.Todos.id == todo_id).first()

    return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})

''' update todo based on todo_id upon validation of user'''
@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(request: Request, todo_id: int, db: Session = Depends(get_db), title: str = Form(...), description: str = Form(...)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo_model = db.query(models.Todos).filter(
        models.Todos.id == todo_id).first()

    todo_model.title = title
    todo_model.description = description

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

''' delete todo based on todo_id upon validation of user'''
@router.get("/delete/{todo_id}", response_class=HTMLResponse)
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(
        models.Todos.owner_id == user.get("id")).first()

    if todo_model is None:
        return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()

    db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)
