from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    #  πεδία που απαιτεί η βάση
    role: str
    first_name: str
    last_name: str
    phone: str
    address: str
    afm: str

class Token(BaseModel):
    access_token: str
    token_type: str