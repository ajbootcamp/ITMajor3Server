from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional
from datetime import date, datetime
from enum import Enum

# Base model for Users
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True  

# Model for User Login
class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None

# Base model for Goals
class GoalBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[date] = None 

class GoalCreate(GoalBase):
    @validator('deadline')
    def check_deadline(cls, value):
        if value and value < date.today(): 
            raise ValueError('Deadline must be today or in the future.')
        return value

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[date] = None

class GoalResponse(GoalBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

# Enum for Goal Status
class GoalStatus(str, Enum):
    incomplete = "Incomplete"
    ongoing = "Ongoing"
    completed = "Completed"

# Base model for Goal Progress
class MilestoneBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: GoalStatus

class MilestoneCreate(MilestoneBase):
    goal_id: int

class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[GoalStatus] = None

class MilestoneResponse(MilestoneBase):
    id: int
    goal_id: int

    class Config:
        orm_mode = True

# Request model for adding a new comment
class CommentCreate(BaseModel):
    user_id: int
    goal_id: Optional[int] = None
    comment_text: str

# Response model for displaying comments
class CommentResponse(BaseModel):
    id: int
    user_id: int
    goal_id: Optional[int]
    comment_text: str
    created_at: str

class CommentUpdate(BaseModel):
    goal_id: Optional[int] = None
    comment_text: Optional[str] = None
