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


class Result(BaseModel):
    user_id: str
    timestamp: datetime.datetime
    type: str
    variable: str
    value: float


class Measurement(BaseModel):
    user_id: str
    timestamp: datetime.datetime
    type: str
    variable: str
    value: float
    metadata: Optional[dict] = {"time_taken_ms": 100, "research": 0}


class Single_measurement(BaseModel):
    timestamp: datetime.datetime
    type: str
    variable: str
    value: float
    metadata: Optional[dict] = {"time_taken_ms": 100, "research": 0}


class Multiple_measurements(BaseModel):
    user_id: str
    measurements: list[Single_measurement]


@router.post(
    "/add-result",
    dependencies=[Depends(bearer.has_access)],
    tags=["internal"],
    include_in_schema=True,
)
def add_result(
    Request: Request,
    result_provided: Result,
    session: Session = Depends(db.get_session),
):
    Variable = models.Variable
    User = models.User
    Result_Type = models.Result_Type
    Result = models.Result
    # Check if type and variable are valid
    statement = select(Variable).where(Variable.id == result_provided.variable)
    variable_check = session.exec(statement).first()
    statement = select(Result_Type).where(Result_Type.id == result_provided.type)
    type_check = session.exec(statement).first()
    if variable_check is None or type_check is None:
        raise HTTPException(status_code=400, detail="Invalid type or variable")
    # Check if user_id is valid
    salt = os.environ["Foreign_key_salt"]
    foreign_key_with_salt = str(result_provided.user_id) + str(salt)
    hashed_key = hashlib.sha256(str(foreign_key_with_salt).encode("utf-8")).hexdigest()
    user_id_check = session.query(User).filter(User.external_id == hashed_key).first()
    user_id = user_id_check.id
    if not user_id_check:
        raise HTTPException(status_code=400, detail="User_id is invalid")
    # Check if result is already in the database and returns the id
    statement = (
        select(Result)
        .where(Result.user_id == user_id)
        .where(Result.variable == result_provided.variable)
        .where(Result.type == result_provided.type)
        .where(Result.timestamp == result_provided.timestamp)
    )
    result_check = session.exec(statement).first()
    if result_check:
        raise HTTPException(status_code=400, detail="Result is already in the database")

    # Insert result into database
    inserted_result = Result(
        user_id=user_id,
        timestamp=result_provided.timestamp,
        type=result_provided.type,
        variable=result_provided.variable,
        value=result_provided.value,
    )
    session.add(inserted_result)
    session.commit()
    session.refresh(inserted_result)
    return {"Status": "Success", "Response": {"id": inserted_result.id}}


@router.post(
    "/add-measurement",
    dependencies=[Depends(bearer.has_access)],
    tags=["internal"],
    include_in_schema=True,
)
def add_measurement(
    Request: Request,
    measurement_provided: Measurement,
    session: Session = Depends(db.get_session),
):
    Variable = models.Variable
    User = models.User
    Measurement_type = models.Measurement_type
    Measurement = models.Measurement
    Measurement_metadata = models.Measurement_metadata
    # Check if type and variable are valid
    statement = select(Variable).where(Variable.name == measurement_provided.variable)
    variable_check = session.exec(statement).first()
    statement = select(Measurement_type).where(
        Measurement_type.name == measurement_provided.type
    )
    type_check = session.exec(statement).first()
    if variable_check is None or type_check is None:
        raise HTTPException(status_code=400, detail="Invalid type or variable")
    variable_id = variable_check.id
    type_id = type_check.id
    # Check if user_id is valid
    salt = os.environ["Foreign_key_salt"]
    foreign_key_with_salt = str(measurement_provided.user_id) + str(salt)
    hashed_key = hashlib.sha256(str(foreign_key_with_salt).encode("utf-8")).hexdigest()
    user_id_check = session.query(User).filter(User.external_id == hashed_key).first()
    if not user_id_check:
        raise HTTPException(status_code=400, detail="User_id is invalid")
    user_id = user_id_check.id
    # Check if measurement is already in the database and returns the id
    statement = (
        select(Measurement)
        .where(Measurement.user_id == user_id)
        .where(Measurement.variable == variable_id)
        .where(Measurement.type == type_id)
        .where(Measurement.timestamp == measurement_provided.timestamp)
    )
    measurement_check = session.exec(statement).first()
    if not measurement_check:
        # Insert measurement into database
        inserted_measurement = Measurement(
            user_id=user_id,
            timestamp=measurement_provided.timestamp,
            type=type_id,
            variable=variable_id,
            value=measurement_provided.value,
        )
        session.add(inserted_measurement)
        session.commit()
        session.refresh(inserted_measurement)
        id = inserted_measurement.id
        measurement_provided_already_in_database = False
    else:
        id = measurement_check.id
        measurement_provided_already_in_database = True
    number_of_metadata = 0
    number_of_metadata_inserted = 0
    for key, value in measurement_provided.metadata.items():
        number_of_metadata += 1
        print("%s: %s" % (key, value))
        # check if type exists in database
        statement = select(Measurement_type).where(Measurement_type.name == key)
        metadata_type_check = session.exec(statement).first()
        if metadata_type_check is None:
            raise HTTPException(
                status_code=400, detail="Invalid metadata type: %s" % key
            )
        # check if metadata is already in the database
        metadata_type_id = metadata_type_check.id
        statement = (
            select(Measurement_metadata)
            .where(Measurement_metadata.measurement_id == id)
            .where(Measurement_metadata.metadata_type == metadata_type_id)
        )
        metadata_check = session.exec(statement).first()
        # insert metadata into database
        if not metadata_check:
            inserted_metadata = Measurement_metadata(
                measurement_id=id, metadata_type=metadata_type_id, value=value
            )
            session.add(inserted_metadata)
            session.commit()
            session.refresh(inserted_metadata)
            number_of_metadata_inserted += 1
    if measurement_provided_already_in_database and number_of_metadata_inserted == 0:
        raise HTTPException(
            status_code=400, detail="Mesurment and metadata is already in the database"
        )
    return {
        "Status": "Success",
        "Response": {
            "id": id,
            "Number of metadata entries": number_of_metadata,
            "Number of metadata entries inserted": number_of_metadata_inserted,
        },
    }


@router.post(
    "/add-measurements",
    dependencies=[Depends(bearer.has_access)],
    tags=["internal"],
    include_in_schema=True,
)
def add_measurements(
    Request: Request,
    measurements_provided: Multiple_measurements,
    session: Session = Depends(db.get_session),
):
    User = models.User
    Measurement = models.Measurement
    salt = os.environ["Foreign_key_salt"]
    foreign_key_with_salt = str(measurements_provided.user_id) + str(salt)
    hashed_key = hashlib.sha256(str(foreign_key_with_salt).encode("utf-8")).hexdigest()
    user_id_check = session.query(User).filter(User.external_id == hashed_key).first()
    if not user_id_check:
        raise HTTPException(status_code=400, detail="User_id is invalid")
    user_id = user_id_check.id
    statement = select(Measurement).where(Measurement.user_id == user_id)
    db_measurements = session.exec(statement).all()
    measurements_in_database = []
    for i in db_measurements:
        measurements_in_database.append(i)
    print(measurements_in_database)
    for measurement in measurements_provided.measurements:
        print(measurement)
        if measurement in measurements_in_database:
            print("Measurement is already in the database")
        else:
            print("Measurement is not in the database")
    return {"Status": measurements_provided.measurements}
