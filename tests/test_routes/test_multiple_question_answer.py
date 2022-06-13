from fastapi.testclient import TestClient
import os, sys
from tests.config import delete_models
from app.database.db import create_language_table

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *

from pydantic import BaseModel

def test_locks(client: TestClient):
    response = client.get("/question_answer")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}
    response = client.post("/question_answer")
    assert response.status_code == 403
    response = client.put("/question_answer")
    assert response.status_code == 403

def test_add_a_question(client: TestClient):
    delete_models()
    create_language_table()
    load_dotenv()
    DB_con = os.environ["DB_test_con"]
    DATABASE_URL = DB_con
    engine = create_engine(DATABASE_URL, echo=True)
    with Session(engine) as session:
        new_question_answer_group = models.Multiple_choice_question_answer_group(
            id = 1,
            description = "Test Multi-QA-Group"
        )
        session.add(new_question_answer_group)
        session.commit()

        new_text_id = models.Text_id(id=1)
        session.add(new_text_id)
        session.commit()

        new_text = models.Text(id=1, text="Hello", text_id=1, language_id=1)
        session.add(new_text)
        session.commit()
    
    params = {
            'answer_group': 1,
            'text_id': 1,
            'number_in_row': 1
    }
    response = client.post(
        "/question_answer",
        headers = {
            "Authorization": "Bearer " + "Let me in",
            "Content-Type": "application/json; charset=utf-8",
            "accept": "application/json",
        },
        json = params
    )
    assert response.status_code == 200
    assert response.json() == {'result': 'Add QA group Success'}

def test_edit_question_answer(client: TestClient):
    delete_models()
    create_language_table()
    load_dotenv()
    DB_con = os.environ["DB_test_con"]
    DATABASE_URL = DB_con
    engine = create_engine(DATABASE_URL, echo=True)
    with Session(engine) as session:
        new_question_answer_group = models.Multiple_choice_question_answer_group(
            id = 1,
            description = "Test Multi-QA-Group"
        )
        session.add(new_question_answer_group)
        session.commit()

        new_text_id = models.Text_id(id=1)
        session.add(new_text_id)
        session.commit()

        new_text = models.Text(id=1, text="Hello", text_id=1, language_id=1)
        session.add(new_text)
        session.commit()

        new_question_answer = models.Multiple_choice_question_answer(id=1, answer_group=1, text_id=1, number_in_row=1)
        session.add(new_question_answer)
        session.commit()

    params = {
        'id': 1,
        'answer_group': 1,
        'text_id': 1,
        'number_in_row': 2
    }

    response = client.put(
        "/question_answer",
        headers={
            "Authorization": "Bearer " + "Let me in",
            "Content-Type": "application/json; charset=utf-8",
            "accept": "application/json",
        },
        json= params,
    )
        
    assert response.status_code == 200

def test_delete_question_answer(client: TestClient):
    delete_models()
    create_language_table()
    load_dotenv()
    DB_con = os.environ["DB_test_con"]
    DATABASE_URL = DB_con
    engine = create_engine(DATABASE_URL, echo=True)
    with Session(engine) as session:
        new_question_answer_group = models.Multiple_choice_question_answer_group(
            id = 1,
            description = "Test Multi-QA-Group"
        )
        session.add(new_question_answer_group)
        session.commit()

        new_text_id = models.Text_id(id=1)
        session.add(new_text_id)
        session.commit()

        new_text = models.Text(id=1, text="Hello", text_id=1, language_id=1)
        session.add(new_text)
        session.commit()

        new_question_answer = models.Multiple_choice_question_answer(id=1, answer_group=1, text_id=1, number_in_row=1)
        session.add(new_question_answer)
        session.commit()
    
    response = client.delete(
        "/question_answer",
        headers={
            "Authorization": "Bearer " + "Let me in",
            "Content-Type": "application/json; charset=utf-8",
            "accept": "application/json",
        },
        params={"id": 1},
    )
    assert response.status_code == 200

def test_get_a_question_answer_with_id(client: TestClient):
    delete_models()
    create_language_table()
    load_dotenv()
    DB_con = os.environ["DB_test_con"]
    DATABASE_URL = DB_con
    engine = create_engine(DATABASE_URL, echo=True)
    with Session(engine) as session:
        new_question_answer_group = models.Multiple_choice_question_answer_group(
            id = 1,
            description = "Test Multi-QA-Group"
        )
        session.add(new_question_answer_group)
        session.commit()

        new_text_id = models.Text_id(id=1)
        session.add(new_text_id)
        session.commit()

        new_text = models.Text(id=1, text="Hello", text_id=1, language_id=1)
        session.add(new_text)
        session.commit()

        new_question_answer = models.Multiple_choice_question_answer(id=1, answer_group=1, text_id=1, number_in_row=1)
        session.add(new_question_answer)
        session.commit()
    
    response = client.get(
        "/question_answer",
        headers={
            "Authorization": "Bearer " + "Let me in",
            "Content-Type": "application/json; charset=utf-8",
            "accept": "application/json",
        },
        params={"id": 1},
    )
    assert response.status_code == 200

def test_get_qa_group(client: TestClient):
    delete_models()
    create_language_table()
    load_dotenv()
    DB_con = os.environ["DB_test_con"]
    DATABASE_URL = DB_con
    engine = create_engine(DATABASE_URL, echo=True)
    with Session(engine) as session:
        new_question_answer_group = models.Multiple_choice_question_answer_group(
            id = 1,
            description = "Test Multi-QA-Group 1"
        )
        session.add(new_question_answer_group)
        session.commit()

        new_question_answer_group = models.Multiple_choice_question_answer_group(
            id = 2,
            description = "Test Multi-QA-Group 2"
        )
        session.add(new_question_answer_group)
        session.commit()

    response = client.get(
        "/question_answer_group",
        headers={
            "Authorization": "Bearer " + "Let me in",
            "Content-Type": "application/json; charset=utf-8",
            "accept": "application/json",
        },
    )
    assert response.status_code == 200