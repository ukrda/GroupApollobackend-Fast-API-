from fastapi.testclient import TestClient
import os, sys
from tests.config import delete_models
from app.database.db import create_language_table

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *


def test_locks(client: TestClient):
    response = client.post("/text/add-text")
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}
    response = client.post("/text/add-translation")
    assert response.status_code == 403
    response = client.put("/text/edit-text")
    assert response.status_code == 403


def test_add_text(client: TestClient):
    delete_models()
    create_language_table()
    params = {
        "text": "Hello",
    }
    response = client.post(
        "/text/add-text",
        headers={
            "Authorization": "Bearer " + "Let me in",
            "Content-Type": "application/json; charset=utf-8",
            "accept": "application/json",
        },
        params=params,
    )
    assert response.status_code == 200


def test_add_translation(client: TestClient):
    delete_models()
    create_language_table()
    load_dotenv()
    DB_con = os.environ["DB_test_con"]
    DATABASE_URL = DB_con
    engine = create_engine(DATABASE_URL, echo=True)
    with Session(engine) as session:
        text_id = models.Text_id(id=1)
        session.add(text_id)
        session.commit()
        text = models.Text(text="Hello", text_id=1, language_id=1)
        session.add(text)
        session.commit()
    response = client.post(
        "/text/add-translation",
        headers={
            "Authorization": "Bearer " + "Let me in",
            "Content-Type": "application/json; charset=utf-8",
            "accept": "application/json",
        },
        json={"text_id": 1, "language_code": "is", "text": "Halló"},
    )
    assert response.status_code == 200


def test_edit_text(client: TestClient):
    delete_models()
    create_language_table()
    load_dotenv()
    DB_con = os.environ["DB_test_con"]
    DATABASE_URL = DB_con
    engine = create_engine(DATABASE_URL, echo=True)
    with Session(engine) as session:
        text_id = models.Text_id(id=1)
        session.add(text_id)
        session.commit()
        text = models.Text(text="Hella", text_id=1, language_id=1)
        session.add(text)
        session.commit()
    response = client.put(
        "/text/edit-text",
        headers={
            "Authorization": "Bearer " + "Let me in",
            "Content-Type": "application/json; charset=utf-8",
            "accept": "application/json",
        },
        json={"text_id": 1, "language_code": "en", "text": "Hello"},
    )
    assert response.status_code == 200


def test_get_text(client: TestClient):
    delete_models()
    create_language_table()
    load_dotenv()
    DB_con = os.environ["DB_test_con"]
    DATABASE_URL = DB_con
    engine = create_engine(DATABASE_URL, echo=True)
    with Session(engine) as session:
        text_id = models.Text_id(id=1)
        session.add(text_id)
        session.commit()
        text = models.Text(text="Hello", text_id=1, language_id=1)
        session.add(text)
        session.commit()
    params = {"text_id": 1, "language_id": 1}
    response = client.get(
        "/text/text",
        headers={
            "Authorization": "Bearer " + "Let me in",
            "Content-Type": "application/json; charset=utf-8",
            "accept": "application/json",
        },
        params=params,
    )
    assert response.status_code == 200
    assert response.json() == {"Text": "Hello"}


def test_get_texts(client: TestClient):
    delete_models()
    create_language_table()
    load_dotenv()
    DB_con = os.environ["DB_test_con"]
    DATABASE_URL = DB_con
    engine = create_engine(DATABASE_URL, echo=True)
    with Session(engine) as session:
        text_id = models.Text_id(id=1)
        session.add(text_id)
        session.commit()
        text_id = models.Text_id(id=2)
        session.add(text_id)
        session.commit()
        text = models.Text(text="Hello", text_id=1, language_id=1)
        session.add(text)
        session.commit()
        text = models.Text(text="Bye", text_id=2, language_id=1)
        session.add(text)
        session.commit()
    params = {"language_code": "en"}
    response = client.get(
        "/text/texts",
        headers={
            "Authorization": "Bearer " + "Let me in",
            "Content-Type": "application/json; charset=utf-8",
            "accept": "application/json",
        },
        params=params,
    )
    assert response.status_code == 200
    assert response.json() == {"1": "Hello", "2": "Bye"}
