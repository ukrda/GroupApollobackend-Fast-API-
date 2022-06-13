import fastapi
from app.database import db
from sqlmodel import Session
from app.models import models
from sqlmodel import Session, select, SQLModel
from fastapi import Depends, HTTPException, Request
from app.security import bearer
from app.database import db
import json
from app.database.db import get_session
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

router = fastapi.APIRouter()


class Translation(SQLModel):
    text_id: int
    language_code: str
    text: str


class Edit_text(SQLModel):
    text_id: int
    text: str
    language_code: str


@router.post(
    "/text/add-text",
    dependencies=[Depends(bearer.has_access)],
    tags=["Text"],
    include_in_schema=True,
    description="Add english text to the database",
)
def add_text(text: str, session: Session = Depends(get_session)):
    # Check if text is already in the database and returns the id
    Text = models.Text
    statement = select(Text).where(Text.text == text).where(Text.language_id == 1)
    results = session.exec(statement)
    Old_text = results.first()
    if Old_text:
        return {"Text already exist": {"Id": Old_text.text_id}}
    # Createse a new text id
    Text_id = models.Text_id()
    session.add(Text_id)
    session.commit()
    session.refresh(Text_id)
    # Inserst the new text into the database
    Text = models.Text(language_id=1, text=text, text_id=int(Text_id.id))
    session.add(Text)
    # TODO: fix this try except block
    try:
        session.commit()
        session.refresh(Text)
    except:
        db.fix_database_text()
        try:
            session.commit()
            session.refresh(Text)
        except:
            raise HTTPException(status_code=500, detail="Database error")
    return {"New text": Text}


@router.post(
    "/text/add-translation",
    dependencies=[Depends(bearer.has_access)],
    tags=["Text"],
    include_in_schema=True,
)
def add_translation(
    Translation_provided: Translation, session: Session = Depends(get_session)
):
    Language = models.Language
    # Get the language id from the languag_code
    language_code = Translation_provided.language_code
    statement = select(Language).where(Language.language_code == language_code)
    results = session.exec(statement)
    language_id = results.first().id
    if language_id is None:
        raise HTTPException(status_code=400, detail="Language not found")
    # Check if text is already in the database and returns the id
    Text = models.Text
    statement = (
        select(Text)
        .where(Text.text_id == Translation_provided.text_id)
        .where(Text.language_id == language_id)
    )
    results = session.exec(statement)
    Old_text = results.first()
    if Old_text:
        return {"Text already exist": {"Id": Old_text.text_id}}
    # Check if text_id is valid and returns the id
    Text_id = models.Text_id
    statement = select(Text_id).where(Text_id.id == Translation_provided.text_id)
    results = session.exec(statement)
    text_id = results.first()
    if text_id is None:
        return {"Text id is not valid": {"Id": Translation_provided.text_id}}

    # Inserst the new text into the database
    new_text = Translation_provided.text

    Text = models.Text(
        language_id=language_id,
        text=new_text,
        text_id=int(Translation_provided.text_id),
    )
    session.add(Text)
    session.commit()
    session.refresh(Text)
    return {"New text": Text}


@router.put(
    "/text/edit-text",
    dependencies=[Depends(bearer.has_access)],
    tags=["Text"],
    include_in_schema=True,
    description="Add english text to the database",
)
def edit_text(edit_text: Edit_text, session: Session = Depends(get_session)):
    # Check if previous text is in the database and returns the id
    Text = models.Text
    statement = (
        select(Text)
        .where(Text.text_id == edit_text.text_id)
        .where(Text.language_id == 1)
    )
    results = session.exec(statement)
    Old_text = results.first()
    if Old_text is None:
        return {"Text not found": {"Id": edit_text.text_id}}
    # Find the text in the database and edit it
    statement = (
        select(Text)
        .where(Text.text_id == edit_text.text_id)
        .where(Text.language_id == 1)
    )
    results = session.exec(statement)
    text = results.first()
    text.text = edit_text.text
    session.commit()
    session.refresh(text)
    return {"New text": text}


@router.get(
    "/text/text",
    dependencies=[Depends(bearer.has_access)],
    tags=["Text"],
    include_in_schema=True,
    description="Get a text from the database",
)
def get_text(text_id: int, language_id: int, session: Session = Depends(get_session)):
    # Get a single text from the database using text_id and language_id
    Text = models.Text
    statement = (
        select(Text)
        .where(Text.text_id == text_id)
        .where(Text.language_id == language_id)
    )
    results = session.exec(statement)
    text = results.first()
    if text is None:
        return {"Text not found": {"Id": text_id}}
    return {"Text": text.text}


@router.get(
    "/text/texts",
    dependencies=[Depends(bearer.has_access)],
    tags=["Text"],
    include_in_schema=True,
    description="Get all texts from the database",
)
def get_texts(language_code: str, session: Session = Depends(get_session)):
    # Get all texts from the database using language_code
    Language = models.Language
    statement = select(Language).where(Language.language_code == language_code)
    results = session.exec(statement)
    language_id = results.first().id
    if language_id is None:
        return {"Language not found": {"Code": language_code}}
    Text = models.Text
    statement = select(Text).where(Text.language_id == language_id)
    results = session.exec(statement)
    texts = results.all()
    all_texts = {}
    for text in texts:
        all_texts[text.text_id] = text.text
    json_compatible_item_data = jsonable_encoder(all_texts)
    return JSONResponse(content=json_compatible_item_data)
