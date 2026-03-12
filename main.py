from fastapi import FastAPI, Request, HTTPException, status # status is used to return the status code of the response AND HTTPException is used to raise an exception when the post is not found
from fastapi.exceptions import RequestValidationError # RequestValidationError is used to handle the validation error when the post_id is not an integer and return a custom error message instead of the default validation error message
from fastapi.responses import JSONResponse # JSONResponse is used to return a JSON response when the post is not found instead of the default HTML response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException # StarletteHTTPException is used to handle the 404 error when the post is not found and return a custom error page instead of the default 404 page



from typing import Annotated
from fastapi import Depends # Depends is used to declare a dependency in the API endpoint, which allows us to inject a database session into the endpoint function. It is used in the get_db function in database.py to create a new session and yield it for use in the API endpoints.
from sqlalchemy.orm import Session # Session is used to create a database session for querying the database and performing CRUD operations on the database. It is used in the get_db function in database.py to create a new session and yield it for use in the API endpoints.
from sqlalchemy import select # its new in SQLAlchemy 2.0 and is used to create a select statement for querying the database. eg db.query() - older version of SQLAlchemy, select() - newer version of SQLAlchemy 2.0

import models
from database import get_db, engine, Base
from schemas import PostCreate, PostResponse, UserCreate, UserResponse

Base.metadata.create_all(bind=engine) # This line creates the database tables based on the models defined in the models.py file. It uses the metadata of the Base class to create the tables in the database. The bind parameter is used to specify the database engine that will be used to create the tables. In this case, it uses the engine defined in database.py, which is a SQLite database.

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")


@app.get("/",include_in_schema=False , name='home')
@app.get("/posts",include_in_schema=False , name='posts')
def home(request: Request):
    return templates.TemplateResponse(
         request ,
        "home.html",
        {"posts": posts, "title": "Home"},
    )

@app.get("/posts/{post_id}",include_in_schema=False) # include_in _schema=False is used to exclude this endpoint from the OpenAPI schema, which means it won't appear in the API documentation. This is useful for endpoints that are meant to serve HTML templates and are not part of the API.
def post_page(request: Request, post_id: int):
    for post in posts:
        if post["id"] == post_id:
                title = post['title'][:50]
                return templates.TemplateResponse(
                    request ,
                    "post.html",
                    {"post": post, "title": title},
                )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")


@app.post(
        "/api/users",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED,
        )
def create_user(user: UserCreate , db: Annotated[Session, Depends(get_db)]):
    # This block of code executes a SQL query to check if a user with the same username already exists in the database.
    #  It uses the select function from SQLAlchemy to create a select statement that queries the User table for a user with the same username as the one being created.
    #  The result of the query is stored in the result variable, and existing_user is set to the first result of the query, which will be the existing user if it exists, or None if it doesn't exist.
    result = db.execute( 
        select(models.User).where(models.User.username == user.username), 
    )
    existing_user = result.scalars().first() # scalars() is used to extract the scalar values from the result of the query, which in this case is the User object. first() is used to get the first result of the query, which will be the existing user if it exists, or None if it doesn't exist.
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists. Please choose a different username.",
        )
    
    # This block of code executes a SQL query to check if a user with the same email already exists in the database.
    #  It uses the select function from SQLAlchemy to create a select statement that queries the User table for a user with the same email as the one being created.
    #  The result of the query is stored in the result variable, and existing_email is set to the first result of the query, which will be the existing user if it exists, or None if it doesn't exist.
    result = db.execute(
        select(models.User).where(models.User.email == user.email),
    )
    existing_email = result.scalars().first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists. Please choose a different email.",
        )
    new_user = models.User(
        username=user.username,
        email=user.email,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)


    return new_user


@app.get("/api/posts", response_model=list[PostResponse]) # response_model is used to specify the model that will be used to validate the response data and return a JSON response with the validated data. In this case, it will return a list of PostResponse models.
def get_posts():
    return posts


# This endpoint is used to create a new post. It takes a PostCreate model as input, which is used to validate the input data when creating a new post. The new post is then added to the posts list and returned as a PostResponse model with the generated id and date_posted fields.
@app.post(
        "/api/posts",
        response_model=PostResponse,
        status_code=status.HTTP_201_CREATED,
        ) # response_model is used to specify the model that will be used to validate the response data and return a JSON response with the validated data. In this case, it will return a PostResponse model. status_code is used to specify the status code of the response when a new post is created.
def create_post(post: PostCreate):
    new_id = max(p['id'] for p in posts) + 1 if posts else 1
    new_post = {
        "id": new_id,
        "author": post.author,
        "title": post.title,
        "content": post.content,
        "date_posted": "March 10, 2026",
        }
    posts.append(new_post)
    return new_post


@app.get("/api/posts/{post_id}", response_model=PostResponse) # response_model is used to specify the model that will be used to validate the response data and return a JSON response with the validated data. In this case, it will return a PostResponse model.
def get_post(post_id: int):
    for post in posts:
        if post["id"] == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found.")
       

# This exception handler will catch all the HTTPException raised in the application and return a custom error message when the post is not found. If the request is made to an API endpoint, it will return a JSON response with the error message. If the request is made to a non-API endpoint, it will return an HTML response with a custom error page.
@app.exception_handler(StarletteHTTPException)
def general_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. please check your request and try again."
    )

    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message}
        )
    
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )

# This exception handler will catch all the RequestValidationError raised in the application and return a custom error message when the post_id is not an integer. If the request is made to an API endpoint, it will return a JSON response with the error message. If the request is made to a non-API endpoint, it will return an HTML response with a custom error page.
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},

        )
    
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )

