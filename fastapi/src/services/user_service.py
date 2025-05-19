import bcrypt
import jwt
from fastapi import HTTPException, status
from sqlalchemy import Engine, create_engine, insert, Table, Column, Integer, String, MetaData
from typing import Optional

from src.config.config import ALGORITHM, SECRET_KEY



# Tabloyu oluştur
metadata = MetaData()
users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True),
    Column("password", String),
    Column("name", String),
    Column("Fullname", String)
)




def encode_payload(payload: dict) -> str:
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def find_one(username: str):
    with Engine.connect() as conn:
        result = conn.execute(
            users_table.select().where(users_table.c.username == username)
        )
        return result.first()  # SQLAlchemy Row objesi döner veya None

def sign_in(params: dict) -> dict:
    username = params.get("username")
    password = params.get("password")
    user = find_one(username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı"
        )

    stored_password = user.password
    if isinstance(stored_password, str):
        stored_password = stored_password.encode()

    if not bcrypt.checkpw(password.encode(), stored_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı adı veya şifre hatalı"
        )

    token = encode_payload({"userId": user.id})
    user_dict = {
        "id": user.id,
        "username": user.username,
        "password": user.password,  # hash dışarı verilmez
        "name": user.name,
        "Fullname": user.Fullname
    }
    return {"token": token, "user": user_dict}

def register(params: dict) -> dict:
    fullname = params.get("fullname")
    username = params.get("username")
    password = params.get("password")
    name = params.get("name")

    if find_one(username):
        raise HTTPException(status_code=400, detail="Kullanıcı adı zaten mevcut")

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    with Engine.begin() as conn:
        stmt = insert(users_table).values(
            name=name,
            username=username,
            Fullname=fullname,
            password=hashed_password
        )
        result = conn.execute(stmt)
        new_user_id = result.inserted_primary_key[0]

    return {"msg": "Kayıt başarılı", "username": username, "id": new_user_id}
