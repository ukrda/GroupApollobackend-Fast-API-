from typing import Optional
import datetime

from sqlmodel import Field, SQLModel, UniqueConstraint


class User(SQLModel, table=True):
    """Users have an id and external id that is a string."""

    __table_args__ = (UniqueConstraint("external_id"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: str


class Variable(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("name"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str


class Result(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    timestamp: datetime.datetime = Field(default=datetime.datetime.utcnow())
    type: int = Field(foreign_key="result_type.id")
    variable: int = Field(foreign_key="variable.id")
    value: float


class Measurement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    timestamp: datetime.datetime = Field(default=datetime.datetime.utcnow())
    type: int = Field(foreign_key="measurement_type.id")
    variable: int = Field(foreign_key="variable.id")
    value: float


class Result_Type(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("name"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str


class Answer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime.datetime = Field(default=datetime.datetime.utcnow())
    user_id: int = Field(foreign_key="user.id")
    time_taken_ms: Optional[float] = Field(default=None)
    answer: Optional[str] = Field(default=None)


class Language(SQLModel, table=True):
    # Table that has the languages that are supported by the app
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    language_code: str


class Text_id(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class Text(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("text_id", "language_id"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    language_id: int = Field(foreign_key="language.id")
    text_id: int = Field(foreign_key="text_id.id")


class Multiple_choice_test(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("name"), UniqueConstraint("test_id"))
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    test_id: int = Field(foreign_key="test.id")


class Multiple_choice_question_answer_group(SQLModel, table=True):
    # Table that has the answer groups for multiple choice questions
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str


class Multiple_choice_question(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    multiple_choice_test: int = Field(foreign_key="multiple_choice_test.id")
    answer_group: int = Field(foreign_key="multiple_choice_question_answer_group.id")
    flipped: bool = Field(default=False, nullable=False)


class Multiple_choice_question_answer(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("answer_group", "number_in_row"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    answer_group: Optional[int] = Field(
        default=None, foreign_key="multiple_choice_question_answer_group.id"
    )
    text_id: int = Field(foreign_key="text_id.id")
    number_in_row: int


class Multiple_choice_question_text_placement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)


class multiple_choice_question_text(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: int = Field(default=None, foreign_key="multiple_choice_question.id")
    text_id: int = Field(default=None, foreign_key="text_id.id")
    placement: int = Field(
        default=None, foreign_key="multiple_choice_question_text_placement.id"
    )


class Multiple_choice_question_completed(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(default=None, foreign_key="user.id")
    question_id: int = Field(default=None, foreign_key="multiple_choice_question.id")
    timestamp: datetime.datetime = Field(default=datetime.datetime.utcnow())


class Measurement_type(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str


class Measurement_metadata(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    measurement_id: int = Field(foreign_key="measurement.id")
    metadata_type: int = Field(foreign_key="measurement_type.id")
    value: float


class Questionnaire(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    valid_pause_hours: int
    description: str


class Test_type(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str


class Test(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    test_type: int = Field(foreign_key="test_type.id")
    name: str
    description: str


class Track(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str


class Track_test(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("track_id", "test_id", "number_in_row"),)
    id: Optional[int] = Field(default=None, primary_key=True)
    track_id: int = Field(foreign_key="track.id")
    test_id: int = Field(foreign_key="test.id")
    repeat_time_hours: float = Field(default=720.0)
    number_in_row: int


class Test_completed(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    test_id: int = Field(foreign_key="test.id")
    timestamp: datetime.datetime = Field(default=datetime.datetime.utcnow())
