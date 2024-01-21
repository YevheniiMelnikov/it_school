from sqlalchemy import Boolean, Column, Integer, String
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
