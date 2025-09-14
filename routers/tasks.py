from datetime import datetime, timedelta, timezone
from typing import Optional, List

from bson import ObjectId
from fastapi import APIRouter, status, HTTPException, Query, Depends
from db.models.tasks import Task
from db.schemas.tasks import task_schema, task_schemas
from db.client import db_client

from routers.authenticate import current_user

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}}
)


# GET
@router.get("/tasks/")
async def show_tasks(
    filter: Optional[List[str]] = Query(default=None),
    user: dict = Depends(current_user)
):
    
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not filter:
        return task_schemas(db_client["tasks"]["tasks"].find({"owner": user["username"]}))


    tags = []
    for f in filter:
        tags.extend(f.split(","))

    return task_schemas(db_client["tasks"]["tasks"].find({
        "owner": user["username"],
        "tags": {"$in": tags}
        })
        )


# POST
@router.post("/task/", response_model=Task)
async def new_task(
    task: Task,
    user: dict = Depends(current_user)          
):

    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    existing_task = db_client["tasks"]["tasks"].find_one({
        "owner": user["username"],
        "title": task.title
        })
    
    if existing_task:

        raise HTTPException(status_code=400, detail="Two tasks cannot have the same title!")


    # Due date must be later then right now
    if task.expire < datetime.now(timezone.utc):

        raise HTTPException(status_code=400, detail="The due date must be later than now!")

    # Add task
    
    task_dict = {
        "owner": user["username"],
        "title": task.title,
        "description": task.description,
        "tags": task.tags,
        "expire": task.expire
    }


    id = db_client["tasks"]["tasks"].insert_one(task_dict).inserted_id

    
    return task



# PATCH
@router.patch("/task/")
async def modify_date(
    task_id: str,
    user: dict = Depends(current_user)
    ):

    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    obj_id = ObjectId(task_id)

    task = db_client["tasks"]["tasks"].find_one({"_id": obj_id})

    if not task:

        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update task

    now = datetime.now()
    date_tomorrow = now + timedelta(days=1)

    db_client["tasks"]["tasks"].update_one(
    {"_id": obj_id},
    {"$set": {"expire": date_tomorrow}})

    return {"detail": "Deadline has been updated!"}


# DELETE
@router.delete("/task/{task_id}")
async def complete_task(
    task_id: str,
    user: dict = Depends(current_user)
    ):

    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    obj_id = ObjectId(task_id)

    task = db_client["tasks"]["tasks"].find_one({"_id": obj_id})

    if not task:

        raise HTTPException(status_code=404, detail="Task not found")
    
    # Delete task

    db_client["tasks"]["tasks"].delete_one({"owner": user["username"]})

    return {"detail": "Task has been removed!"}