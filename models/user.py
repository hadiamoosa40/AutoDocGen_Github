from pydantic import BaseModel

class User(BaseModel):
    github_id: int
    username: str
    token: str