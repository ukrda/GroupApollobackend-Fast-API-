import fastapi
from app.database import db
from sqlmodel import Session
from app.models import models
from sqlmodel import Field, Relationship, Session, select
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPBasicCredentials
from hashlib import sha256
from dotenv import load_dotenv
import os

security = HTTPBearer()
load_dotenv()


def check_api_key(api_key: str):
    api_key_hashed = sha256(api_key.encode("utf-8")).hexdigest()
    Hased_data_api_key = os.environ["Hased_data_api_key"]
    Dev_mode = os.environ["Dev_mode"]
    if api_key_hashed == Hased_data_api_key or Dev_mode == "True":
        return True
    else:
        return False


def has_access(credentials: HTTPBasicCredentials = Depends(security)):
    if check_api_key(credentials.credentials) == False:
        raise HTTPException(
            status_code=401,
            detail="Invalid Bearer token",
        )


def get_token(header):
    bearer, _, token = header.partition(" ")
    if bearer != "Bearer":
        raise ValueError("Invalid token")
    return token
