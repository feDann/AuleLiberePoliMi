from beanie import Document, Indexed, Link
from typing import Optional
from pydantic import List, BaseModel

class Preferences(BaseModel):
    """The user preferences model."""
    campus: Optional[str]
    duration: Optional[int]

class SearchHistory(Document):
    """The user search history model."""
    telegram_id: int
    start_time: Optional[int]
    end_time: Optional[int]
    campus: Optional[str]
    day: Optional[str]


class User(Document):
    telegram_id = Indexed(int)
    chat_id = Indexed(int)
    first_name = Optional[str]
    last_name = Optional[str]
    username = Optional[str]
    preferences = Optional[Preferences]
    latest_search = Optional[SearchHistory]