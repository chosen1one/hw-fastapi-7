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


'''
@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/signup")
def get_signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup")
def post_user(
    email: str = Form(),
    full_name: str = Form(),
    password: str = Form(),
):
    payload = User(email=email, full_name=full_name, password=password)
    users_repository.save(payload)
    response = Response(status_code=200)
    response.set_cookie()
    return RedirectResponse("/login", status_code=303)

@app.get("/login")
def get_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def post_login(
    request: Request,
    response: Response,
    email: str = Form(),
    password: str = Form()
):
    user = users_repository.get_by_email(email)
    if user.password == password:
        response = RedirectResponse("/profile", status_code=303)
        token = encode_jwt(user.id)
        response.set_cookie("token", token)
        return response
    return Response("Permission Denied!", status_code=404)

@app.get("/profile")
def get_profile(request: Request, token: str = Cookie()):
    user_id = decode_jwt(token)
    user = users_repository.get_by_id(int(user_id))
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
        }
    )

@app.get("/flowers")
def get_flowers(request: Request):
    flowers = flowers_repository.get_all()
    return templates.TemplateResponse(
        "flowers.html",
        {
            "request": request,
            "flowers": flowers,
        }
    )

@app.post("/flowers")
def post_flowers(
    name: str = Form(),
    count: int = Form(),
    cost: int = Form()
):
    payload = Flower(name=name, count=count, cost=cost)
    flowers_repository.save(payload)
    return RedirectResponse("/flowers", status_code=303)

@app.get("/cart/items")
def get_items(
    request: Request,
    response: Response,
    cart: str = Cookie(default="[]")
):
    cart_json = json.loads(cart)

    flowers = [flowers_repository.get_by_id(id) for id in cart_json]
    total = sum(flower.cost for flower in flowers)

    return templates.TemplateResponse(
        "cart.html",
        {
            "request": request,
            "cart": flowers,
            "total": total
        }
    )

@app.post("/cart/items")
def post_items(
    request: Request,
    response: Response,
    flower_id: int = Form(),
    cart: str = Cookie(default="[]")
):
    cart_json = json.loads(cart)
    if flower_id:
        cart_json.append(flower_id)
        new_cart = json.dumps(cart_json)
        resp = RedirectResponse("/flowers", status_code=303)
        resp.set_cookie(key="cart", value=new_cart)
    return resp

'''