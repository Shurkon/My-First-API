from pydantic import BaseModel
import datetime


class Task(BaseModel):

    title: str
    description: str
    tags: list
    expire: datetime.datetime