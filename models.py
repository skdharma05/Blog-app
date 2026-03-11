from __future__ import annotations # This import allows us to use the Post class in the User class before it is defined. 
                                    # It enables forward references, which means we can refer to a class that has not been defined yet.
                                    #  In this case, it allows us to define the relationship between the User and Post models without having to worry about the order of their definitions.

from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    image_file: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        default=None,
    )

    # This relationship is used to define the relationship between the User and Post models. 
    # It allows us to access the posts associated with a user using user.posts, 
    # and it also allows us to access the author of a post using post.author.
    #  The back_populates parameter is used to specify the name of the attribute on the related model that will be used to access the relationship from the other side.
    #  In this case, it means that we can access the author of a post using post.
    # author, and we can access the posts of a user using user.posts.
    posts: Mapped[list[Post]] = relationship(back_populates="author") 


    @property 
    def image_path(self) -> str: # This property method is used to return the path to the user's profile picture. 
                                # If the user has an image_file specified, it returns the path to that image. If not, it returns the path to a default profile picture.
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), # This is a foreign key that references the id column in the users table. It establishes a relationship between the Post and User models, allowing us to associate each post with a specific user.
        nullable=False,
        index=True, # This creates an index on the user_id column, which can improve query performance when filtering posts by user_id.
    )
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC), # This sets the default value of the date_posted column to the current date and time in UTC when a new post is created.
                                             # The lambda function is used to ensure that the default value is evaluated at the time of post creation, rather than at the time of model definition.
    )

    author: Mapped[User] = relationship(back_populates="posts")
    # This relationship is used to define the relationship between the Post and User models. 
    # It allows us to access the author of a post using post.
    # author, and it also allows us to access the posts associated with a user using user.posts.
    # The back_populates parameter is used to specify the name of the attribute on the related model that will be used to access the relationship from the other side.
    #  In this case, it means that we can access the author of a post using post.
    # author, and we can access the posts of a user using user.posts.
