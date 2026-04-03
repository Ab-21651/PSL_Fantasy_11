from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserInDB(User):
    hashed_password: str
