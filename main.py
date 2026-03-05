from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()
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
@app.get("/",response_class=HTMLResponse)
@app.get("/posts",response_class=HTMLResponse,include_in_schema=False)
def home():
    return f"<h1>{posts[0]['title']}</h1>"

@app.get("/api/posts")
def get_posts():
    return posts