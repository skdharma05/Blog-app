from fastapi import FastAPI, Request, HTTPException, status # status is used to return the status code of the response AND HTTPException is used to raise an exception when the post is not found
from fastapi.exceptions import RequestValidationError # RequestValidationError is used to handle the validation error when the post_id is not an integer and return a custom error message instead of the default validation error message
from fastapi.responses import JSONResponse # JSONResponse is used to return a JSON response when the post is not found instead of the default HTML response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException # StarletteHTTPException is used to handle the 404 error when the post is not found and return a custom error page instead of the default 404 page

from schemas import PostCreate, PostResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

posts : list[dict] = [
    {
        "id": 1,
        "title": "Introduction to FastAPI",
        "author": "Alice",
        "content": "FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.",
        "tags": ["fastapi", "python", "api"],
        "published": True,
        "views": 150,
        "date_posted": "March 9, 2026" 
    },
    {
        "id": 2,
        "title": "Understanding Python Lists and Dictionaries",
        "author": "Bob",
        "content": "Python lists and dictionaries are versatile data structures used to store collections of items. Lists are ordered, dictionaries are key-value pairs.",
        "tags": ["python", "data structures", "tutorial"],
        "published": False,
        "views": 85,
        "date_posted": "March 9, 2026" 
    }
]


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

