from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional

import postgres_communication

app = FastAPI()

SECRET_KEY = "b3e7b3b3e7b3b3e7b3e7"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TokenData(BaseModel):
    user_id: int

class User(BaseModel):
    user_id: int
    password: str
    loyalty_card_id: int

class Transaction(BaseModel):
    user_id: int
    coupon_value: Optional[int] = None

def hash_password(password: str):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=400, detail="Invalid token")
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")
    return token_data

def get_current_user(token_data: TokenData = Depends(verify_token)):
    user = postgres_communication.get_user(token_data.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/create/user/")
def api_create_user(user: User):
    try:
        hashed_password = hash_password(user.password)
        postgres_communication.create_user(user.user_id, user.loyalty_card_id, hashed_password)
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/")
def api_list_users():
    logging.debug("Received a request")
    try:
        users = postgres_communication.list_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/coupons/{loyalty_card_id}")
def read_coupons(loyalty_card_id: int):
    try:
        coupons = postgres_communication.get_coupons(loyalty_card_id)
        return coupons
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/{user_id}")
def api_delete_user(user_id: int):
    try:
        postgres_communication.delete_user(user_id)
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transactions/")
def api_make_transaction(transaction: Transaction):
    try:
        print("Coupon Value:", transaction.coupon_value)
        postgres_communication.make_transaction(transaction.user_id, transaction.coupon_value)
        return {"message": "Transaction recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))