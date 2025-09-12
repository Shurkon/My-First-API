from fastapi import FastAPI
from routers import tasks
from routers import authenticate

app = FastAPI()

app.include_router(tasks.router)
app.include_router(authenticate.router)