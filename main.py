from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


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
        "views": 150
    },
    {
        "id": 2,
        "title": "Understanding Python Lists and Dictionaries",
        "author": "Bob",
        "content": "Python lists and dictionaries are versatile data structures used to store collections of items. Lists are ordered, dictionaries are key-value pairs.",
        "tags": ["python", "data structures", "tutorial"],
        "published": False,
        "views": 85
    }
]


@app.get("/",include_in_schema=False , name='home')
@app.get("/posts",include_in_schema=False , name='posts')
def home(request: Request):
    return templates.TemplateResponse(request , "home.html", {"posts": posts, "title": "Home"},)

@app.get("/api/posts")
def get_posts():
    return posts