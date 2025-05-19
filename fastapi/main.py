from fastapi import FastAPI
from src.database.database import Base, engine
from src.router.users_router import router as users_router



Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users_router, prefix="/users")
