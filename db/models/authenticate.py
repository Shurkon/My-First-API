from pydantic import BaseModel

class User(BaseModel):

    username: str


class UserPassword(User):

    password: str


class NewPassword(BaseModel):

    username: str
    new_password: str