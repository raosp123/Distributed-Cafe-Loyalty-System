from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import postgres_communication

app = FastAPI()

# conn, cur = postgres_communication.get_db_connection()

class User(BaseModel):
    user_id: int
    loyalty_card_id: int

class Transaction(BaseModel):
    user_id: int


@app.post("/users/")
def api_create_user(user: User):
    try:
        postgres_communication.create_user(user.user_id, user.loyalty_card_id)
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/")
def api_list_users():
    try:
        users = postgres_communication.list_users()
        return users
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
        postgres_communication.make_transaction(transaction.user_id)
        return {"message": "Transaction recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
