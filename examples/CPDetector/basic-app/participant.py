from pydantic import BaseModel
from typing import Optional


class Participant(BaseModel):
    name: str = None
    subjects: str = None
    grade: str = None
    gender: Optional[str] = None
