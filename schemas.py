from typing import List, Optional
from pydantic import BaseModel, EmailStr


class PostTodo(BaseModel):
    title: str

class UserCreate(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    user_id: str
    name: str
    email: EmailStr

class UserLogin(BaseModel):
    email: str
    password: str

class PromptHistoryCreate(BaseModel):
    user_id: str
    r_recipe_name: str

class PromptHistoryResponse(BaseModel):
    id: str
    user_id: str
    r_recipe_name: str