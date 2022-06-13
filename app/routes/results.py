import os
import fastapi
from typing import Optional
from app.database import db
from app.security import bearer
from sqlmodel import Session
from app.models import models
from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel
from hashlib import sha256
from sqlmodel import Field, Relationship, Session, select
from app.models import models
import json

engine = db.get_engine()

router = fastapi.APIRouter()


class Requested_type(BaseModel):
    user_id: str
    time: Optional[int]


@router.post(
    "/results",
    dependencies=[Depends(bearer.has_access)],
    tags=["Results"],
    include_in_schema=True,
)
def add_result(
    Request: Request,
    Requested_type: Requested_type,
    session: Session = Depends(db.get_session),
):
    salt = os.environ["Foreign_key_salt"]
    foreign_key_with_salt = str(Requested_type.user_id) + str(salt)
    hashed_key = sha256(str(foreign_key_with_salt).encode("utf-8")).hexdigest()
    statement = select(models.User).where(models.User.external_id == hashed_key)
    user = session.exec(statement).first()
    id = user.id
    statement = select(models.Result).where(models.Result.user_id == id)
    results = session.exec(statement)
    results_list = {}
    for result in results:
        results_list[result.id] = {
            "Value": result.value,
            "Timestamp": result.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Type": result.type,
            "Variable": result.variable,
        }
    return results_list
