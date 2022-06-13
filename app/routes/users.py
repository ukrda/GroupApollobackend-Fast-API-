import os
import fastapi
import uuid
import hashlib
from dotenv import load_dotenv
from app.database import db
from sqlmodel import Field, Relationship, Session, select
from app.models import models
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPBasicCredentials
from app.security import bearer

load_dotenv()
salt = os.environ["Foreign_key_salt"]

router = fastapi.APIRouter()

engine = db.get_engine()

user = models.User


@router.get("/add_user", dependencies=[Depends(bearer.has_access)], tags=["users"])
def create_user(Request: Request, session: Session = Depends(db.get_session)):
    foreign_key = uuid.uuid4()
    foreign_key_with_salt = str(foreign_key) + str(salt)
    hashed_key = hashlib.sha256(str(foreign_key_with_salt).encode("utf-8")).hexdigest()
    new_user = user(
        id=None, external_id=str(hashed_key)
    )
    session.add(new_user)
    session.commit()
    return foreign_key
