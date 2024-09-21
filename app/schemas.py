# app/schemas.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# For creating a new user (POST request)
class UserCreate(BaseModel):
    email : EmailStr
    name : str
    password : str
    limit : int
    window_seconds : int

class LoginUserCreate(BaseModel):
    email : EmailStr
    password : str


class CustomerResponse(BaseModel):
    name: str

    class Config:
        orm_mode = True
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    limit : int
    window_seconds : int

    class Config:
        orm_mode = True
        from_attributes = True
