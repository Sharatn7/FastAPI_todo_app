# importing necessary modules
from fastapi import FastAPI, status
import models
from database import engine
from routers import auth, todos
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import uvicorn
# Uvicorn is an ASGI web server implementation for Python.

''' Added the title and description of the app. '''''
app = FastAPI(
    title="Todo App",
    description="Todo App with FastAPI",
)

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

app.include_router(auth.router)
app.include_router(todos.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
