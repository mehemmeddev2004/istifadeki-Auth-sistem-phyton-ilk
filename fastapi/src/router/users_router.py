from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import bcrypt
import jwt

from src.database.database import get_db  # get_db fonksiyonunu başka dosyaya taşıyabilirsin
from src.config.config import ALGORITHM, SECRET_KEY
from src.database.user import User

router = APIRouter()

class UserRegister(BaseModel):
    username: str
    password: str
    name: Optional[str]
    fullname: Optional[str]

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/register")
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Kullanıcı adı zaten var")

    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

    new_user = User(
        username=user.username,
        password=hashed_password,
        name=user.name,
        fullname=user.fullname
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"msg": "Kayıt başarılı", "id": new_user.id}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not bcrypt.checkpw(user.password.encode(), db_user.password.encode()):
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı")

    token = jwt.encode({"userId": db_user.id}, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "token": token,
        "user": {
            "id": db_user.id,
            "username": db_user.username,
            "name": db_user.name,
            "fullname": db_user.fullname
        }
    }
