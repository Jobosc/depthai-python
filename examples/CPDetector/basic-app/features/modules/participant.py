from typing import Optional

from pydantic import BaseModel

from features.modules.timestamps import Timestamps


class Participant(BaseModel):
    id: str
    comments: Optional[str] = None
    timestamps: Optional[Timestamps] = None
