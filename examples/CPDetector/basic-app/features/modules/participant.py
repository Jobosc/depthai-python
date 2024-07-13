from typing import Optional

from pydantic import BaseModel


class Participant(BaseModel):
    id: str = None
    comments: Optional[str] = None
