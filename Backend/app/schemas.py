from pydantic import BaseModel, EmailStr, model_validator
from typing import Optional
from datetime import datetime

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


class EventCreate(BaseModel):
    title: str
    description: str
    capacity: int
    
    vip_tickets: int = 0
    regular_tickets: int = 0

    @model_validator(mode='after')
    def check_ticket_capacity(self):
        # Υπολογίζουμε το συνολικό άθροισμα των εισιτηρίων
        total_tickets = self.vip_tickets + self.regular_tickets
        
        # Το άθροισμα δεν μπορεί να ξεπερνά τη χωρητικότητα
        if total_tickets > self.capacity:
            raise ValueError(
                f"Το άθροισμα των εισιτηρίων ({total_tickets}) δεν μπορεί να "
                f"ξεπερνά τη συνολική χωρητικότητα της εκδήλωσης ({self.capacity})."
            )
        return self


class MessageCreate(BaseModel):
    receiver_id: int
    event_id: Optional[int] = None
    content: str

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    event_id: Optional[int]
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True # για να διαβάζει τα δεδομένα από το SQLAlchemy