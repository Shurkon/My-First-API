from pydantic import BaseModel

class User(BaseModel):

    username: str


class UserPassword(User):

    password: str


class NewPassword(BaseModel):

    new_password: str