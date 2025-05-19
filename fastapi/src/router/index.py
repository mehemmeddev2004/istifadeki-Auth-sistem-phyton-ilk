from pydantic import BaseModel


class LoginModel(BaseModel):
    username: str
    password: str
    
class RegisterModel(BaseModel):
    username: str
    password: str
    fullname: str
    name: str

