from pydantic import BaseModel, EmailStr

class SearchRequest(BaseModel):
    email: EmailStr