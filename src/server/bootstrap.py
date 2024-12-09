from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import huggingface_hub


server = FastAPI()
