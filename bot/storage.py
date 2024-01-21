from typing import Type

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import FlushError

from bot.logger import logger
from bot.models import Base, User


class Storage:
    def __init__(self, db_name):
        self.engine = create_engine(db_name)
        self.session = sessionmaker(bind=self.engine)()
        try:
            Base.metadata.create_all(self.engine)
        except Exception as e:
            logger.exception(f"An error occurred while creating tables: {e}")

    def add_user(self, user_id) -> None:
        try:
            user = User(
                user_id=user_id,
                discount=10,
                name=None,
                phone=None,
                email=None,
                test_passed=False,
            )
            self.session.add(user)
            self.session.commit()
        except (IntegrityError, FlushError):
            self.session.rollback()
            self.update_user_data(
                user_id,
                {
                    "discount": 10,
                    "name": None,
                    "phone": None,
                    "email": None,
                    "test_passed": False,
                },
            )
        except Exception as e:
            logger.exception(f"An error occurred: {e}")
            self.session.rollback()

    def update_user_data(self, user_id: int, data: dict) -> None:
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if not user:
            self.add_user(user_id)
            user = self.session.query(User).filter_by(user_id=user_id).first()

        for field, value in data.items():
            setattr(user, field, value)

        self.session.commit()

    def get_user_by_id(self, user_id: int) -> Type[User] | None:
        try:
            user = self.session.query(User).filter_by(user_id=user_id).one()
            return user
        except NoResultFound:
            logger.info(f"User with user_id={user_id} not found")
            return None

    def give_plus_five(self, user_id: int) -> None:
        user = self.session.query(User).filter_by(user_id=user_id).first()
        if user:
            user.discount += 5
            self.session.commit()

    def check_user_existence(self, user_id: int) -> bool:
        return bool(
            self.session.query(User.user_id).filter_by(user_id=user_id).scalar()
        )

    def close(self) -> None:
        self.session.close()
