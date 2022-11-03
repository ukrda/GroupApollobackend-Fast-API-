from lib2to3.pgen2.tokenize import TokenError
import os
import fastapi
import uuid
import hashlib
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPBasicCredentials
from pydantic import BaseModel
import httpx
import asyncio

import random
import string

from app.database import db
from app.database.db import get_session
from sqlmodel import Session, select
from app.models import models
from app.models.basemodels import UserModel, TokenModel
from app.security import bearer
from app.security.bearer import *


load_dotenv()
salt = os.environ["Foreign_key_salt"]

router = fastapi.APIRouter()

engine = db.get_engine()

User = models.User

# Generate Random String
def generate_random_string():
    password = ''.join(random.choice(string.printable) for i in range(8))

    return password

# Get Token and Sign In
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm=Depends(), session: Session=Depends(get_session)):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.u_name}, expires_delta=access_token_expires
    )
    return {'Status': 'Success', "user": user, "access_token": access_token, "token_type": "bearer"}


@router.post('/allombo_token')
async def get_allombo_token(token: TokenModel, session: Session= Depends(get_session)):
    redirect_uri = os.environ["ALLOMBO_TOKEN_URL"]
    profile_uri = os.environ["ALLOMBO_PROFILE_URL"]

    async with httpx.AsyncClient() as client:
        token_header = {
            'Content-type': 'application/json'
        }
        data = {
            'grant_type': 'authorization_code',
            'client_id': os.environ['ALLOMBO_CLIENT_ID'],
            'client_secret': os.environ['ALLOMBO_CLIENT_SECRET'],
            'redirect_uri': os.environ['ALLOMBO_REDIRECT_URI'],
            'code': token.code,
            'code_verifier': token.code_verifier
        }
        print('code --> ', token.code)
        print('code_verifier --> ', token.code_verifier)

        token_response = await client.post(redirect_uri, data=data)
        print('here =====> ', token_response.status_code)
        print('token_response =====> ', token_response)

        
        if token_response.status_code == 200 and token_response.json()['access_token'] != None:
            profile_header = {
                'Content-type': 'application/json',
                'Authorization': 'Bearer ' + token_response.json()['access_token']
            }
            profile_response = await client.get(profile_uri, headers=profile_header)
            print(profile_response.json())

            # Should check the profile response json data
            allombo_user_name = profile_response.json()['name']
            allombo_user_email = profile_response.json()['email']

            group_user = get_user(allombo_user_name)
            if group_user is None:
                new_user = User(
                    u_name = allombo_user_name,
                    u_password = get_password_hash(generate_random_string()),
                    u_email = allombo_user_email
                )
                session.add(new_user)
                session.commit()

                group_user = new_user

            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": allombo_user_name}, expires_delta=access_token_expires
            )
            return {'Status': 'Success', "user": group_user, "access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=token_response.json(),
                headers={"WWW-Authenticate": "Bearer"},
            )

@router.post(
    '/sign_up',
    # dependencies=[Depends(bearer.get_current_active_user)],
    # tags=["Authentication"],
    # include_in_schema=True,
    # description="Sign up a user",
)
def sign_up_user(userModel: UserModel, session: Session= Depends(get_session)):

    query_result = session.query(User).filter(User.u_name == userModel.u_name).first()

    if query_result is not None:
        return {'Status': 'Success', 'Response': 'Already Exists'}

    try:
        new_user = User(
            u_name = userModel.u_name,
            u_password = get_password_hash(userModel.u_password),
            u_email = userModel.u_email
        )
        session.add(new_user)
        session.commit()

        return {'Status': 'Success', 'Response': 1}
    except:
        return {'Status': 'Fail', 'Response': 'Failed to sign up'}



# @router.get('/sign_in',
#     dependencies=[Depends(bearer.has_access)],
#     tags=["Authentication"],
#     include_in_schema=True,
#     description="Sign in a user",
# )
# def sign_in_user(u_name: str, u_password: str, u_email: str, session: Session = Depends(get_session)):
#     query = select(User).where(
#         User.u_name == u_name,
#         User.u_password == u_password
#     )
#     query_result = session.exec(query).first()

#     if query_result is None:
#         return {"Status": "Success", "Response": "No user"}

#     return {"Status": "Success", "Response": query_result.u_id}

# @router.post(
#     '/sign_up',
#     dependencies=[Depends(bearer.has_access)],
#     tags=["Authentication"],
#     include_in_schema=True,
#     description="Sign up a user",
# )
# def sign_up_user(UserModel: UserModel, session: Session= Depends(get_session)):
#     query = select(User).where(
#         User.u_name == UserModel.u_name
#     )
#     query_result = session.exec(query).first()
#     if query_result is not None:
#         return {'Status': 'Success', 'Response': 'Already Exists'}

#     try:
#         new_user = User(
#             u_name = UserModel.u_name,
#             u_password = UserModel.u_password,
#             u_email = UserModel.u_email
#         )
#         session.add(new_user)
#         session.commit()

#         return {'Status': 'Success', 'Response': 1}
#     except:
#         return {'Status': 'Fail', 'Response': 'Failed to sign up'}

