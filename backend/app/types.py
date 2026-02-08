from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class RequestContext:
    user_id: str

class User(BaseModel):
    id: str
    name: str
    email: str

class Contact(BaseModel):
    id: str
    owner_id: str
    name: str
    email: str
    role: str
    avatar_url: str | None = None