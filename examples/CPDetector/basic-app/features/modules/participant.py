import json
import os
from typing import Optional

from pydantic import BaseModel

from features.modules.timestamps import Timestamps
from utils.parser import ENVParser


class Participant(BaseModel):
    id: str
    comments: Optional[str] = None
    timestamps: Optional[Timestamps] = None

    def store_participant_metadata(self, path: str) -> None:
        json_data = self.model_dump_json()
        with open(os.path.join(path, "metadata.json"), 'w') as file:
            file.write(json_data)


def read_participant_metadata(date: str, person: str) -> "Participant":
    env = ENVParser()
    path = os.path.join(env.main_path, env.temp_path, date, person, "metadata.json")

    load_file = open(path, "r")
    data = json.load(fp=load_file)
    load_file.close()

    return Participant(**data)
