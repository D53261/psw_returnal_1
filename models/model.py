from sqlmodel import Field, Relationship, SQLModel
from typing import Optional
from datetime import date
from decimal import Decimal

class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str
    password: str

class Subscription(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    empresa: str
    site: Optional[str] = None
    data_assinatura: date
    valor: Decimal
    user_id: int = Field(foreign_key='users.id')
    user: Users = Relationship()

class Payments(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    subscription_id: int = Field(foreign_key='subscription.id')
    subscription: Subscription = Relationship()
    date: date
    state: str = Field(default="Funcional")
    user_id: int