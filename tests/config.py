from fastapi.testclient import TestClient
import os
import pytest
from app.main import app
from app.database.db import get_session # should be matched
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, delete
from sqlmodel.pool import StaticPool
from app.models import models


load_dotenv()

@pytest.fixture(name="session")
def session_fixture():
    DB_con = os.environ["DB_test_con"]
    DATABASE_URL = DB_con
    engine = create_engine(DATABASE_URL, echo=True, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session
    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()



# @pytest.fixture(name="session")
# def session_fixture():
#     DB_con = os.environ["DB_test_con"]
#     DATABASE_URL = DB_con
#     engine = create_engine(DATABASE_URL, echo=True)
#     SQLModel.metadata.create_all(engine)
#     with Session(engine) as session:
#         yield session


# @pytest.fixture(name="client")
# def client_fixture(session: Session):
#     def get_session_override():
#         yield session

#     app.dependency_overrides[get_session] = get_session_override
#     client = TestClient(app)
#     yield client
#     app.dependency_overrides.clear()

def delete_model(Model, engine):
    with Session(engine) as session:
        statement = delete(Model)
    result = session.exec(statement)
    session.commit()


def delete_models():
    DB_con = os.environ["DB_test_con"]
    DATABASE_URL = DB_con
    engine = create_engine(DATABASE_URL, echo=True, poolclass=StaticPool)
    delete_model(models.Measurement_metadata, engine)
    delete_model(models.Measurement, engine)
    delete_model(models.Measurement_type, engine)
    delete_model(models.Result, engine)
    delete_model(models.User, engine)
    delete_model(models.Variable, engine)
    delete_model(models.Result_Type, engine)
    delete_model(models.Text, engine)
    delete_model(models.Language, engine)
    delete_model(models.Multiple_choice_question, engine)
    delete_model(models.Multiple_choice_question_answer, engine)
    delete_model(models.Multiple_choice_question_answer_group, engine)
    delete_model(models.Multiple_choice_question_text_placement, engine)
    delete_model(models.Text_id, engine)
    delete_model(models.Test, engine)
    delete_model(models.Test_type, engine)
    delete_model(models.Track_test, engine)
    delete_model(models.Track, engine)