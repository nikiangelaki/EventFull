from pydantic import BaseModel, model_validator, EmailStr
from typing import Optional, List
from datetime import datetime

# --- ΤΥΠΟΙ ΕΙΣΙΤΗΡΙΩΝ (TICKET TYPES) ---

class TicketTypeCreate(BaseModel):
    name: str # π.χ. "VIP", "Student", "General"
    price: float
    quantity: int # Πόσα τέτοια εισιτήρια θα εκδοθούν

class TicketTypeResponse(TicketTypeCreate):
    id: str
    event_id: str
    available: int # Πόσα έμειναν απούλητα

    class Config:
        from_attributes = True

# --- ΕΚΔΗΛΩΣΕΙΣ (EVENTS) ---

class EventCreate(BaseModel):
    title: str
    event_type: str
    venue: str
    address: str
    city: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    start_datetime: datetime
    end_datetime: datetime
    capacity: int
    description: Optional[str] = None
    
    # ΠΡΟΣΟΧΗ: Πλέον παίρνουμε μια ΛΙΣΤΑ με τους τύπους εισιτηρίων!
    tickets: List[TicketTypeCreate]

    @model_validator(mode='after')
    def check_ticket_capacity(self):
        # Υπολογίζουμε το συνολικό άθροισμα όλων των εισιτηρίων της λίστας
        total_tickets = sum(ticket.quantity for ticket in self.tickets)
        
        # Ελέγχουμε αν ξεπερνούν τη συνολική χωρητικότητα
        if total_tickets > self.capacity:
            raise ValueError(
                f"Το άθροισμα των εισιτηρίων ({total_tickets}) δεν μπορεί να "
                f"ξεπερνά τη συνολική χωρητικότητα της εκδήλωσης ({self.capacity})."
            )
        return self

class EventResponse(BaseModel):
    id: str
    organizer_id: int
    title: str
    event_type: str
    venue: str
    address: str
    city: str
    country: str
    start_datetime: datetime
    end_datetime: datetime
    capacity: int
    status: str
    description: Optional[str]
    
    # Επιστρέφει και τα εισιτήρια μαζί με την εκδήλωση!
    ticket_types: List[TicketTypeResponse] = []

    class Config:
        from_attributes = True

# --- ΚΡΑΤΗΣΕΙΣ (BOOKINGS) ---

class BookingCreate(BaseModel):
    ticket_type_id: str # Το Frontend στέλνει ποιο ακριβώς εισιτήριο θέλει
    number_of_tickets: int # Πόσα εισιτήρια τέτοιου τύπου θέλει

class BookingResponse(BaseModel):
    id: str
    attendee_id: int
    event_id: str
    ticket_type_id: str
    time: datetime
    number_of_tickets: int
    total_cost: float
    booking_status: str

    class Config:
        from_attributes = True

# --- ΧΡΗΣΤΕΣ & ΑΥΘΕΝΤΙΚΟΠΟΙΗΣΗ (USERS) ---

class UserCreate(BaseModel):
    username: str
    password: str
    role: str  # "organizer", "participant" ή "admin"
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    afm: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- ΜΗΝΥΜΑΤΑ (MESSAGES) ---

class MessageCreate(BaseModel):
    receiver_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True