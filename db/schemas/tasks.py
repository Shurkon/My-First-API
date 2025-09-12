from datetime import datetime, timezone

def task_schema(task) -> dict:
    return {
        
        "id": str(task["_id"]),
        "title": task["title"],
        "description": task.get("description"),
        "tags": task.get("tags", []),
        "expire": task["expire"],
    
    }

def task_schemas(tasks) -> list:
    return [task_schema(task) for task in tasks]

