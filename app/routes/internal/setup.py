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


class Variable(BaseModel):
    name: str
    description: str


class Result_type(BaseModel):
    name: str
    description: str


class Measurement_type(BaseModel):
    name: str
    description: str


@router.post(
    "/add-variable",
    dependencies=[Depends(bearer.has_access)],
    tags=["internal"],
    include_in_schema=True,
)
def add_variable(
    Request: Request,
    variable_provided: Variable,
    session: Session = Depends(db.get_session),
):
    Variable = models.Variable
    statement = select(Variable).where(Variable.name == variable_provided.name)
    variable_check = session.exec(statement).first()
    if variable_check is not None:
        raise HTTPException(status_code=400, detail="Variable already exists")
    inserted_variable = Variable(
        name=variable_provided.name, description=variable_provided.description
    )
    session.add(inserted_variable)
    session.commit()
    session.refresh(inserted_variable)
    return inserted_variable


@router.post(
    "/add-measurement-type",
    dependencies=[Depends(bearer.has_access)],
    tags=["internal"],
    include_in_schema=True,
)
def add_Measurement_type(
    Request: Request,
    Measurement_type_provided: Measurement_type,
    session: Session = Depends(db.get_session),
):
    Measurement_type = models.Measurement_type
    statement = select(Measurement_type).where(
        Measurement_type.name == Measurement_type_provided.name
    )
    result_type_check = session.exec(statement).first()
    if result_type_check is not None:
        raise HTTPException(status_code=400, detail="Result type already exists")
    inserted_measurement_type = Measurement_type(
        name=Measurement_type_provided.name,
        description=Measurement_type_provided.description,
    )
    session.add(inserted_measurement_type)
    session.commit()
    session.refresh(inserted_measurement_type)
    return inserted_measurement_type
