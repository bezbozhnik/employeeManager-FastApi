from sqlalchemy  import Column, Float, String, DateTime
from db import Base

class Employee(Base):
    __tablename__ = 'employees'

    login = Column(String, primary_key=True)
    password = Column(String)
    salary = Column(Float)
    promotion_date = Column(DateTime)
    token = Column(String)
    token_expiration = Column(DateTime)
    def __repr__(self):
        return f"Employee - {self.login}"
