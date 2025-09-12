from typing import Optional
from sqlmodel import SQLModel, Field, Column, String
from datetime import date, time
from pydantic import BaseModel
from sqlalchemy import Boolean
import uuid
import base64
from uuid import UUID, uuid4

def generate_base64_uuid() -> str:
    u = uuid.uuid4()
    b64 = base64.urlsafe_b64encode(u.bytes).rstrip(b'=').decode('ascii')
    return b64

class Booking(SQLModel, table=True):
    __tablename__ = "bookings"
    
    id: Optional[str] = Field(default_factory=generate_base64_uuid, primary_key=True)
    service: str = Field(sa_column=Column(String, nullable=False))
    category: Optional[str] = Field(default=None, sa_column=Column(String))
    date: date
    time: time
    # date: dt.date = Field(sa_column=Column(Date, nullable=False))
    # time: dt.time = Field(sa_column=Column(Time, nullable=False))
    client_name: str = Field(sa_column=Column(String, nullable=False))
    reference: Optional[str] = Field(default=None, sa_column=Column(String, unique=True, index=True))


class BookingCreate(BaseModel):
    service: str
    category: str | None = None
    date: date
    time: time
    client_name: str

class BookingOut(BookingCreate):
    id: UUID
    reference: str

    class Config:
        orm_mode = True

