import os
import fastapi
from pydantic import BaseModel
from app.database import db
from typing import Optional
from sqlmodel import Session
from app.models import models
from sqlmodel import Field, Relationship, Session, select
from fastapi import Depends, HTTPException, Request
from app.security import bearer
import secrets
from hashlib import sha256
import datetime
from dotenv import load_dotenv
import hashlib
import json

engine = db.get_engine()

router = fastapi.APIRouter()
load_dotenv()


class NextQuestion(BaseModel):
    user_id: str
    track_name: str


@router.post(
    "/next-question",
    dependencies=[Depends(bearer.has_access)],
    tags=["internal"],
    include_in_schema=True,
)
def next_question(
    Request: Request,
    data: NextQuestion,
    session: Session = Depends(db.get_session),
):
    user_id = data.user_id
    salt = os.environ["Foreign_key_salt"]
    foreign_key_with_salt = str(user_id) + str(salt)
    hashed_key = hashlib.sha256(str(foreign_key_with_salt).encode("utf-8")).hexdigest()
    track_name = data.track_name
    with session.begin():
        statement = select(models.User).where(models.User.external_id == hashed_key)
        user = session.exec(statement).first()
        if user == None:
            raise HTTPException(status_code=404, detail="User not found")
    with session.begin():
        statement = select(models.Track).where(models.Track.name == track_name)
        track = session.exec(statement).first()
        if track == None:
            raise HTTPException(status_code=404, detail="Track not found")

    return {
        "Status": "Success",
        "Response": {"Question_id": "test", "Question_text": "test"},
    }
