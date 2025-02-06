"""
This module provides functionality to manage participant metadata.

It defines the Participant class which handles the storage and retrieval of participant metadata.

Classes:
    Participant: Manages participant metadata including ID, comments, and timestamps.

Functions:
    store_participant_metadata: Stores the participant metadata to a file.
    read_participant_metadata: Reads and returns the participant metadata from a file.
"""

import json
import os
from typing import Optional

from pydantic import BaseModel

from utils.parser import ENVParser

env = ENVParser()


class Participant(BaseModel):
    """
    Manages participant metadata including ID, comments, and timestamps.

    Attributes:
        id (str): The ID of the participant.
        comments (Optional[str]): Additional comments about the participant.
    """
    id: str
    comments: Optional[str] = None

    def store_participant_metadata(self, path: str) -> None:
        """
        Stores the participant metadata to a file.

        Args:
            path (str): The path where the metadata file will be stored.
        """
        json_data = self.model_dump_json()
        with open(os.path.join(path, env.metadata_file_name), 'w') as file:
            file.write(json_data)


def read_participant_metadata(date: str, person: str) -> "Participant":
    """
    Reads and returns the participant metadata from a file.

    Args:
        date (str): The date associated with the metadata.
        person (str): The ID of the participant.

    Returns:
        Participant: The participant object with the metadata.
    """
    path = os.path.join(env.main_path, env.temp_path, date, person, env.metadata_file_name)
    load_file = open(path, "r")
    data = json.load(fp=load_file)
    load_file.close()

    return Participant(**data)
