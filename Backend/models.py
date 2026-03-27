from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.orm import declarative_base, relationship
import datetime

# Ορισμός της βασικής κλάσης από την οποία κληρονομούν όλα τα μοντέλα
Base = declarative_base()

# --- ΠΙΝΑΚΑΣ ΣΥΣΧΕΤΙΣΗΣ ΠΟΛΛΑ-ΠΡΟΣ-ΠΟΛΛΑ (Events <-> Categories) ---
# Μία εκδήλωση μπορεί να ανήκει σε πολλές κατηγορίες [cite: 126]
event_category_association = Table(
    'event_has_category', Base.metadata,
    Column('event_id', String(50), ForeignKey('events.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

# --- 1. ΠΙΝΑΚΑΣ ΧΡΗΣΤΩΝ ---
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False) # cite: 21
    password = Column(String(255), nullable=False) # Θα αποθηκεύεται κρυπτογραφημένο # cite: 21
    role = Column(String(20), nullable=False) # Διαχειριστής, Διοργανωτής, Συμμετέχων, Επισκέπτης # cite: 12
    first_name = Column(String(50), nullable=False) # cite: 21
    last_name = Column(String(50), nullable=False) # cite: 21
    email = Column(String(100), unique=True, nullable=False) # cite: 21
    phone = Column(String(20), nullable=False) # cite: 21
    address = Column(String(200), nullable=False) # cite: 21
    latitude = Column(Float, nullable=True) # Γεωγραφική τοποθεσία # cite: 21
    longitude = Column(Float, nullable=True) # Γεωγραφική τοποθεσία # cite: 21
    afm = Column(String(20), nullable=False) # cite: 21
    is_approved = Column(Boolean, default=False) # Για την αναμονή έγκρισης από τον διαχειριστή # cite: 23

    # Συσχετίσεις (Relationships)
    events = relationship("Event", back_populates="organizer")
    bookings = relationship("Booking", back_populates="attendee")
    messages_sent = relationship("Message", foreign_keys='Message.sender_id', back_populates="sender")
    messages_received = relationship("Message", foreign_keys='Message.receiver_id', back_populates="receiver")

# --- 2. ΠΙΝΑΚΑΣ ΚΑΤΗΓΟΡΙΩΝ ΕΚΔΗΛΩΣΗΣ ---
class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False) # π.χ. Music, Live Performance # cite: 78, 79
    
    # Συσχέτιση με τις εκδηλώσεις μέσω του βοηθητικού πίνακα
    events = relationship("Event", secondary=event_category_association, back_populates="categories")

# --- 3. ΠΙΝΑΚΑΣ ΕΚΔΗΛΩΣΕΩΝ ---
class Event(Base):
    __tablename__ = 'events'

    id = Column(String(50), primary_key=True) # Π.χ. "EV1024" σύμφωνα με το XML # cite: 76, 124
    organizer_id = Column(Integer, ForeignKey('users.id')) # Ο διοργανωτής της εκδήλωσης # cite: 141
    title = Column(String(200), nullable=False) # cite: 125
    event_type = Column(String(100), nullable=False) # cite: 127
    venue = Column(String(100), nullable=False) # cite: 128
    address = Column(String(200), nullable=False) # cite: 128
    city = Column(String(100), nullable=False) # cite: 128
    country = Column(String(100), nullable=False) # cite: 128
    latitude = Column(Float, nullable=True) # cite: 129
    longitude = Column(Float, nullable=True) # cite: 129
    start_datetime = Column(DateTime, nullable=False) # χρόνος έναρξης # cite: 130
    end_datetime = Column(DateTime, nullable=False) # χρόνος λήξης # cite: 130
    capacity = Column(Integer, nullable=False) # συνολική χωρητικότητα # cite: 132
    status = Column(String(20), default="DRAFT") # DRAFT, PUBLISHED, COMPLETED, CANCELLED # cite: 142
    description = Column(String(1000), nullable=True) # cite: 142

    # Συσχετίσεις
    organizer = relationship("User", back_populates="events")
    categories = relationship("Category", secondary=event_category_association, back_populates="events")
    ticket_types = relationship("TicketType", back_populates="event", cascade="all, delete-orphan")
    media = relationship("EventMedia", back_populates="event", cascade="all, delete-orphan")

# --- 4. ΠΙΝΑΚΑΣ ΠΟΛΥΜΕΣΩΝ (ΦΩΤΟΓΡΑΦΙΕΣ) ΕΚΔΗΛΩΣΗΣ ---
class EventMedia(Base):
    __tablename__ = 'event_media'

    id = Column(Integer, primary_key=True)
    event_id = Column(String(50), ForeignKey('events.id'))
    photo_path = Column(String(255), nullable=False) # Προαιρετικές φωτογραφίες # cite: 143

    event = relationship("Event", back_populates="media")

# --- 5. ΠΙΝΑΚΑΣ ΤΥΠΩΝ ΕΙΣΙΤΗΡΙΩΝ ---
class TicketType(Base):
    __tablename__ = 'ticket_types'

    id = Column(String(50), primary_key=True) # Π.χ. "T1" # cite: 91
    event_id = Column(String(50), ForeignKey('events.id'))
    name = Column(String(100), nullable=False) # cite: 133
    price = Column(Float, nullable=False) # cite: 133
    quantity = Column(Integer, nullable=False) # Συνολικό πλήθος # cite: 133
    available = Column(Integer, nullable=False) # Διαθέσιμο υπόλοιπο # cite: 133

    # Συσχετίσεις
    event = relationship("Event", back_populates="ticket_types")
    bookings = relationship("Booking", back_populates="ticket_type")

# --- 6. ΠΙΝΑΚΑΣ ΚΡΑΤΗΣΕΩΝ ---
class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(String(50), primary_key=True) # Π.χ. "B501" # cite: 105
    attendee_id = Column(Integer, ForeignKey('users.id')) # Ο χρήστης που έκανε την κράτηση # cite: 135
    time = Column(DateTime, default=datetime.datetime.utcnow) # χρόνος πραγματοποίησης κράτησης # cite: 136
    ticket_type_id = Column(String(50), ForeignKey('ticket_types.id')) # cite: 137
    number_of_tickets = Column(Integer, nullable=False) # cite: 138
    total_cost = Column(Float, nullable=False) # cite: 139
    booking_status = Column(String(20), default="PENDING") # PENDING, CONFIRMED, CANCELLED # cite: 140

    # Συσχετίσεις
    attendee = relationship("User", back_populates="bookings")
    ticket_type = relationship("TicketType", back_populates="bookings")

# --- 7. ΠΙΝΑΚΑΣ ΜΗΝΥΜΑΤΩΝ (Για επικοινωνία) ---
class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id')) # Αποστολέας # cite: 173
    receiver_id = Column(Integer, ForeignKey('users.id')) # Παραλήπτης # cite: 173
    content = Column(String(1000), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    is_read = Column(Boolean, default=False) # Ένδειξη για νέα μηνύματα # cite: 174

    # Συσχετίσεις
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="messages_received")

# --- Δημιουργία της Βάσης (SQLite για ανάπτυξη/δοκιμές) ---
if __name__ == "__main__":
    # Το echo=True τυπώνει στο terminal τις SQL εντολές που τρέχουν στο παρασκήνιο.
    engine = create_engine('sqlite:///event_management.db', echo=True)
    
    # Δημιουργεί όλους τους πίνακες στη βάση αν δεν υπάρχουν ήδη
    Base.metadata.create_all(engine)
    
    print("\n✅ Η βάση δεδομένων και οι πίνακες δημιουργήθηκαν με επιτυχία στο αρχείο 'event_management.db'!")