import os
import fastapi
import uuid
import hashlib
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPBasicCredentials
from pydantic import BaseModel

from app.database import db
from app.database.db import get_session
from sqlmodel import Session, select
from app.models import models
from app.security import bearer


load_dotenv()
salt = os.environ["Foreign_key_salt"]

router = fastapi.APIRouter()

engine = db.get_engine()

User = models.User

class UserModel(BaseModel):
    u_name: str
    u_password: str
    u_email: str
    
@router.get('/sign_in',
    dependencies=[Depends(bearer.has_access)],
    tags=["Authentication"],
    include_in_schema=True,
    description="Sign in a user",
)
def sign_in_user(u_name: str, u_password: str, u_email: str, session: Session = Depends(get_session)):
    query = select(User).where(
        User.u_name == u_name,
        User.u_password == u_password
    )
    query_result = session.exec(query).first()

    if query_result is None:
        return {"Status": "Success", "Response": "No user"}

    return {"Status": "Success", "Response": query_result.u_id}

@router.post(
    '/sign_up',
    dependencies=[Depends(bearer.has_access)],
    tags=["Authentication"],
    include_in_schema=True,
    description="Sign up a user",
)
def sign_up_user(UserModel: UserModel, session: Session= Depends(get_session)):
    query = select(User).where(
        User.u_name == UserModel.u_name
    )
    query_result = session.exec(query).first()
    if query_result is not None:
        return {'Status': 'Success', 'Response': 'Already Exists'}

    try:
        new_user = User(
            u_name = UserModel.u_name,
            u_password = UserModel.u_password,
            u_email = UserModel.u_email
        )
        session.add(new_user)
        session.commit()

        return {'Status': 'Success', 'Response': 1}
    except:
        return {'Status': 'Fail', 'Response': 'Failed to sign up'}


# @router.get("/add_user", dependencies=[Depends(bearer.has_access)], tags=["users"])
# def create_user(Request: Request, session: Session = Depends(db.get_session)):
#     foreign_key = uuid.uuid4()
#     foreign_key_with_salt = str(foreign_key) + str(salt)
#     hashed_key = hashlib.sha256(str(foreign_key_with_salt).encode("utf-8")).hexdigest()
#     new_user = user(
#         id=None, external_id=str(hashed_key)
#     )
#     session.add(new_user)
#     session.commit()
#     return foreign_key

