from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Literal
from typing import List, Literal, Optional
from mlx_lm import load, stream_generate
from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()

server = FastAPI()
