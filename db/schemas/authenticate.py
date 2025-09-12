def user_schema(user) -> dict:

    return {

        "username": user["username"],
        "password": user["password"]

    }

def users_schemas(users) -> list:

    return [user_schema(user) for user in users]