import json
from jose import jwt

from fastapi import Cookie, FastAPI, Form, Request, Response, templating, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from typing import List

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

flowers_repository = FlowersRepository()
purchases_repository = PurchasesRepository()
users_repository = UsersRepository()


class UserRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str

class UserResponse(BaseModel):
    email: EmailStr
    full_name: str


def encode_jwt(user_id: int) -> str:
    payload = { "user_id": user_id }
    token = jwt.encode(payload, "chosenone")
    return token

def decode_jwt(token: str) -> int:
    payload = jwt.decode(token, "chosenone")
    return payload["user_id"]


@app.post("/signup")
def post_signup(user: UserRequest):
    payload = User(user.email, user.full_name, user.password)
    users_repository.save(payload)
    return user

@app.post("/login")
def post_login(username: str = Form(), password: str = Form()):
    user = users_repository.get_by_email(username)
    if not user or user.password != password:
        return HTTPException(status_code=400, detail="Wrong username or password!")
    token = encode_jwt(user.id)
    return {"access_token": token, "type": "bearer"}

@app.get("/profile", response_model=UserResponse)
def get_profile(token: str = Depends(oauth2_scheme)):
    user_id = decode_jwt(token)
    user = users_repository.get_by_id(user_id)
    return user

class FlowerResponse(BaseModel):
    name: str
    count: int
    cost: int

class FlowerRequest(BaseModel):
    name: str
    count: int
    cost: int

@app.get("/flowers", response_model=List[FlowerResponse])
def get_flowers(request: Request):
    flowers = flowers_repository.get_all()
    return flowers

@app.post("/flowers")
def post_flowers(flower: FlowerRequest):
    payload = Flower(flower.name, flower.count, flower.cost)
    flower = flowers_repository.save(payload)
    return flower.id

@app.post("/cart/items")
def post_items(
    response: Response,
    flower_id: int = Form(),
    cart_items: str = Cookie(default="[]")
):
    cart_items = json.loads(cart_items)
    cart_items.append(flower_id)
    cart_items.json.dumps(cart_items)
    response.set_cookie(key="cart_items", value=cart_items)
    return {}

@app.get("/cart/items")
def get_items(
    request: Request,
    cart_items: str = Cookie(default="[]")
):
    cart_items = json.loads(cart_items)
    flowers = [flowers_repository.get_by_id(id) for id in cart_json]
    total = sum(flower.cost for flower in flowers)
    return {
        "flowers": [{"name": flower.name, "cost": flower.cost, "count": flower.count} for flower in flowers],
        "Total Price": total
    }