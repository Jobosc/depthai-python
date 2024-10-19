from pydantic import BaseModel
from datetime import datetime


class TimeWindow(BaseModel):
    start: datetime
    end: datetime