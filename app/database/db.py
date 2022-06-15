"""Connections to database, and function to create database tables if they don't exist."""
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, select
from app.models import models


def get_engine():
    load_dotenv()
    DB_con = os.environ["DB_con"]
    DATABASE_URL = DB_con
    return create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(get_engine())


def get_session():
    load_dotenv()
    DB_con = os.environ["DB_con"]
    DATABASE_URL = DB_con
    engine = create_engine(DATABASE_URL, echo=True)
    with Session(engine) as session:
        yield session


# def fix_database_text():
#     """Add data into text tables if data does not already exist"""
#     load_dotenv()
#     DB_con = os.environ["DB_test_con"]
#     DATABASE_URL = DB_con
#     engine = create_engine(DATABASE_URL, echo=True)
#     Language = models.Language
#     with Session(engine) as session:
#         statement = select(Language).where(Language.id == 1)
#         results = session.exec(statement)
#         first_lang = results.first()
#         if first_lang is None:
#             language = models.Language(id=1, name="English", language_code="en")
#             session.add(language)
#             session.commit()


# def create_language_table():
#     load_dotenv()
#     DB_con = os.environ["DB_test_con"]
#     DATABASE_URL = DB_con
#     engine = create_engine(DATABASE_URL, echo=True)
#     with Session(engine) as session:
#         language = models.Language(id=1, name="English", language_code="en")
#         session.add(language)
#         session.commit()
#         language = models.Language(id=2, name="Icelandic", language_code="is")
#         session.add(language)
#         session.commit()
