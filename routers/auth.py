
# importing necessary modules
from fastapi import Depends, HTTPException, status, APIRouter, Request, Response, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
from typing import Optional
import secrets
import sys
sys.path.append("..")

'''Data validation and settings management using python type annotations. pydantic enforces type hints at runtime, and provides user friendly errors when data is invalid.

https://docs.python.org/3/library/typing.html

Helper for hashing passwords using different algorithms. - https: // passlib.readthedocs.io/en/stable/lib/passlib.context.html

secrets module is used to generate cryptographically strong random numbers suitable for managing data such as passwords,
 account authentication, security tokens, and related secrets. Ex: SECRET_KEY = secrets.token_hex(16)"
 '''

SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"

'''CryptContext is a helper class for managing multiple password hashing algorithms. It provides a single interface for hashing 
and verifying passwords using a variety of algorithms.'''

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

''' Jinja2Templates is a helper class for using Jinja2 templates with FastAPI. It provides a single interface for loading'''
templates = Jinja2Templates(directory="templates")

''' APIRouter is a class that helps you organize a group of related routes.'''
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)

''' LoginForm is a class that is used to create a login form.'''


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")


''' SessionLocal is a class that is used to create a local session.'''


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


''' get_password_hash is a function that is used to get the password hash.'''


def get_password_hash(password):
    return bcrypt_context.hash(password)


''' verify_password is a function that is used to verify the password.'''


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


''' authenticate_user is a function that is used to authenticate the user.'''


def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users)\
        .filter(models.Users.username == username)\
        .first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


''' create_access_token is a function that is used to create the access token.'''
''' jwt is a JSON Web Token implementation in Python. It supports both encoding and decoding of JWTs.'''


def create_access_token(username: str, user_id: int,
                        expires_delta: Optional[timedelta] = None):

    encode = {"sub": username, "id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=10)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


'''get_current_user is a function that is used to get the current user.'''


async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            logout(request)
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="Not Found")


# login and return the token.
@router.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False
    token_expires = timedelta(minutes=15)
    token = create_access_token(user.username,
                                user.id,
                                expires_delta=token_expires)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return True


@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

''' login is a function that is used to login the user. It takes in the request and db as parameters.
 It calls the login_for_access_token which creates the access token and sets the cookie.'''


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(
            url="/todos", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = "Incorrect username or password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        return response
    except HTTPException:
        msg = "Unkown Error"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


''' logout is a function that is used to logout the user. It takes in the request as a parameter and deletes the access_token cookie.'''


@router.get("/logout")
async def logout(request: Request):
    msg = "Logout Successful"
    response = templates.TemplateResponse(
        "login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    return response


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


''' register_user is a function that is used to register the user. 
It takes in the request, email, username, firstname, lastname, password, verify_password and db as parameters.
It validates the username and email to check if they are already taken.
Validation1 is a variable that is used to check if the username is already taken.
Validation2 is a variable that is used to check if the email is already taken.
If the password and verify_password do not match, it returns a message that says "Passwords do not match".
If the username is already taken, it returns a message that says "Username already taken".
If the email is already taken, it returns a message that says "Email already taken".
If the username and email are not taken, it creates a new user and returns a message that says "Registration Successful".
'''


@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, email: str = Form(...), username: str = Form(...), firstname: str = Form(...), lastname: str = Form(...),
                        password: str = Form(...), verify_password: str = Form(...), db: Session = Depends(get_db)):

    validation1 = db.query(models.Users).filter(
        models.Users.username == username).first()

    validation2 = db.query(models.Users).filter(
        models.Users.email == email).first()

    if password != verify_password:
        msg = "Passwords do not match"
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})
    if validation1 is not None:
        msg = "Username already taken"
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})
    if validation2 is not None:
        msg = "Email-id already taken"
        return templates.TemplateResponse("register.html", {"request": request, "msg": msg})

    user_model = models.Users()
    user_model.username = username
    user_model.email = email
    user_model.first_name = firstname
    user_model.last_name = lastname
    hash_password = get_password_hash(password)
    user_model.hashed_password = hash_password
    db.add(user_model)
    db.commit()

    msg = "User successfully created"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
