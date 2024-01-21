from dataclasses import dataclass
from typing import Any

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    discount = Column(Integer)
    name = Column(String)
    phone = Column(String)
    email = Column(String)
    test_passed = Column(Boolean, default=False)

    def __repr__(self):
        return f"User(user_id={self.user_id}, discount={self.discount}, name={self.name}, phone={self.phone}, email={self.email}, test_passed={self.test_passed})"


@dataclass
class Question:
    id: int
    message: str
    options: tuple[dict[str, Any]]
    answer: str
    image: str

    @property
    def option_buttons(self):
        return [option["button"] for option in self.options]


@dataclass
class Quiz:
    id: int
    name: str
    questions: list[Question]

    @classmethod
    def parse(cls, data: dict) -> "Quiz":
        questions = [Question(**i) for i in data["questions"]]
        id = data["id"]
        name = data["name"]
        return Quiz(id=id, questions=questions, name=name)

    def get_question(self, id: int) -> Question:
        for question in self.questions:
            if question.id == id:
                return question


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer)
    user_id = Column(Integer)
    question_id = Column(Integer)
    answer = Column(String)
