from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from db.models.authenticate import User, UserPassword, NewPassword
from db.client import db_client
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

# Sensitive data (I would place this in the environment variables)
ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 30
SECRET = "80c3b395483a4255b2a18c42d5b61523a541fadfdc60dc6ef55daca790115f90"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2 = OAuth2PasswordBearer(tokenUrl="login")



router = APIRouter(
    prefix="/authenticate",
    tags=["authenticate"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}}
)


def current_user(token: str = Depends(oauth2)):

    exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de invalidas",
                headers={"WWW-Authenticate": "Bearer"}
            )

    try:

        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:

            raise exception
        
    except JWTError:

        raise exception


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)




# LOGIN
@router.post("/login/")
async def login(form: OAuth2PasswordRequestForm = Depends()):

    match = db_client["users"]["users"].find_one(           
        {"username": form.username},
        {"username": 1, "password": 1}     
    )

    if not match:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User or password do not match")
    
    
    if not pwd_context.verify(form.password, match["password"]):

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User or password do not match")
    
    access_token = {

        "sub": match["username"],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_DURATION)

    }

    return {
        
        "access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM),
        "token_type": "bearer"

    }



# REGISTER
@router.post("/register/")
async def register(user: UserPassword):

    match = db_client["users"]["users"].find_one({"username": user.username})

    if match:

        raise HTTPException(status_code=400, detail="Username already taken") # Is this the correct status code?
    
    hashed = hash_password(user.password)

    dictionary = {"username": user.username, "password": hashed}

    db_client["users"]["users"].insert_one(dictionary)

    return {"username": user.username}



# CHANGE PASSWORD (Quizas pueda usar el nombre del token) (Implementar un sistema para introducir el password otra vez)
@router.patch("/changepassword/")
async def changepassword(data: NewPassword, user: User = Depends(current_user)):


    hashed = hash_password(data.new_password)

    db_client["users"]["users"].update_one(
    {"username": data.username},
    {"$set": {"password": hashed}})



# DELETE USER (and tasks)
