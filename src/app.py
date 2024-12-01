from routes import chat, not_implemented
from fastapi import FastAPI

app = FastAPI()

app.include_router(chat.router)
app.include_router(not_implemented.router)
