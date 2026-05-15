from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str


class BookCreate(BaseModel):
    id: str
    author: str
    name: str
    note: str
    serial: str


class BookResponse(BaseModel):
    id: str
    author: str
    name: str
    note: str
    serial: str
