import fastapi
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

from pydantic import BaseModel

router = fastapi.APIRouter()

class New_QA(BaseModel):
    answer_group: int
    text_id: int
    number_in_row: int

class Edit_QA(BaseModel):
    id: int
    answer_group: int
    text_id: int
    number_in_row: int


@router.post(
    "/question_answer",
    dependencies=[Depends(bearer.has_access)],
    tags=["Question and Answer"],
    include_in_schema=True,
    description="Add a Q&A to the database",
)
def add_question_answer(New_QA: New_QA, session: Session = Depends(get_session)):
    # Check question_answer_group
    QA_group = models.Multiple_choice_question_answer_group
    statement = select(QA_group).where(QA_group.id == New_QA.answer_group)
    qa_results = session.exec(statement).first()
    if qa_results is None:
        return {'result': 'no question answer group'}
    
    # Check Text
    Text = models.Text
    statement = select(Text).where(Text.id == New_QA.text_id)
    text_results = session.exec(statement).first()
    if text_results is None:
        return {'result': 'no text'}
    
    # Add a QA_group
    QA = models.Multiple_choice_question_answer(
        answer_group = New_QA.answer_group,
        text_id = New_QA.text_id,
        number_in_row = New_QA.number_in_row
    )
    session.add(QA)
    session.commit()

    return {'result': 'Add QA group Success'}

@router.put(
    "/question_answer",
    dependencies=[Depends(bearer.has_access)],
    tags=["Question and Answer"],
    include_in_schema=True,
    description="Edit a Q&A in the database",
)
def edit_question_answer(Edit_QA: Edit_QA, session: Session = Depends(get_session)):
    # Check QA
    QA = models.Multiple_choice_question_answer
    statement = select(QA).where(QA.id == Edit_QA.id)
    results = session.exec(statement)
    check_QA = results.first()
    
    if check_QA:
        # Check question_answer_group
        QA_group = models.Multiple_choice_question_answer_group
        statement = select(QA_group).where(QA_group.id == Edit_QA.answer_group)
        check_QA_group = session.exec(statement).first()

        if check_QA_group is None:
            return {'result': 'No QA Group'}
        
        # Check Text
        Text = models.Text
        statement = select(Text).where(Text.id == Edit_QA.text_id)
        check_Text = session.exec(statement).first()
        
        if check_Text is None:
            return {'result': 'No Text'}
        
        # Edit
        check_QA.answer_group = Edit_QA.answer_group
        check_QA.text_id = Edit_QA.text_id
        check_QA.number_in_row = Edit_QA.number_in_row

        session.add(check_QA)
        session.commit()

        return {'result': 'Edit'}
    else:
        return {'result': 'No QA'}

@router.delete(
    "/question_answer",
    dependencies=[Depends(bearer.has_access)],
    tags=["Question and Answer"],
    include_in_schema=True,
    description="Delete a Q&A in the database",
)
def delete_question_answer(id: int, session: Session = Depends(get_session)):
    # Check QA
    QA = models.Multiple_choice_question_answer
    statement = select(QA).where(QA.id == id)
    results = session.exec(statement)
    check_QA = results.first()

    if check_QA:
        # Delete
        session.delete(check_QA)
        session.commit()

        return {'result': 'Delete'}
    else:
        return {'result': 'No QA to Delete'}

@router.get(
    "/question_answer",
    dependencies=[Depends(bearer.has_access)],
    tags=["Question and Answer"],
    include_in_schema=True,
    description="Get a Q&A in the database",
)
def get_question_answer(id: int, session: Session = Depends(get_session)):
    # Check QA
    QA = models.Multiple_choice_question_answer
    statement = select(QA).where(QA.id == id)
    results = session.exec(statement)
    check_QA = results.first()
    if check_QA:
        return {
            'result': {
                'id': check_QA.id,
                'answer_group': check_QA.answer_group,
                'text_id': check_QA.text_id,
                'number_in_row': check_QA.number_in_row
            }
        }
    else:
        return {'result': 'No QA'}

@router.get(
    "/question_answer_group",
    dependencies=[Depends(bearer.has_access)],
    tags=["Question and Answer"],
    include_in_schema=True,
    description="Get a Q&A group in the database",
)
def get_question_answer_group(session: Session = Depends(get_session)):
    # Check QA
    QA = models.Multiple_choice_question_answer
    statement = select(QA)
    results_qa = session.exec(statement).all()
    
    result = {}
    for entry in results_qa:
        result[str(entry.id)] = {
            'answer_group': entry.answer_group,
            'text_id': entry.text_id,
            'number_in_row': entry.number_in_row
        }
    
    return result