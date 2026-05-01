from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.orm import relationship
import datetime

# ΣΗΜΑΝΤΙΚΟ: Παίρνουμε το Base από το database.py μας!
from app.database import Base

# --- ΠΙΝΑΚΑΣ ΣΥΣΧΕΤΙΣΗΣ ΠΟΛΛΑ-ΠΡΟΣ-ΠΟΛΛΑ ---
event_category_association = Table(
    'event_has_category', Base.metadata,
    Column('event_id', String(50), ForeignKey('events.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

# --- 1. ΠΙΝΑΚΑΣ ΧΡΗΣΤΩΝ ---
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False) # Προσοχή: Το ονομάζουμε hashed_password για να ταιριάζει με το security.py
    role = Column(String(20), nullable=False) 
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    afm = Column(String(20), nullable=False)
    is_approved = Column(Boolean, default=False)

    events = relationship("Event", back_populates="organizer")
    bookings = relationship("Booking", back_populates="attendee")
    messages_sent = relationship("Message", foreign_keys='Message.sender_id', back_populates="sender")
    messages_received = relationship("Message", foreign_keys='Message.receiver_id', back_populates="receiver")

# --- 2. ΠΙΝΑΚΑΣ ΚΑΤΗΓΟΡΙΩΝ ---
class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    events = relationship("Event", secondary=event_category_association, back_populates="categories")

# --- 3. ΠΙΝΑΚΑΣ ΕΚΔΗΛΩΣΕΩΝ ---
class Event(Base):
    __tablename__ = 'events'

    id = Column(String(50), primary_key=True)
    organizer_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(200), nullable=False)
    event_type = Column(String(100), nullable=False)
    venue = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    capacity = Column(Integer, nullable=False)
    status = Column(String(20), default="DRAFT")
    description = Column(String(1000), nullable=True)

    organizer = relationship("User", back_populates="events")
    categories = relationship("Category", secondary=event_category_association, back_populates="events")
    ticket_types = relationship("TicketType", back_populates="event", cascade="all, delete-orphan")
    media = relationship("EventMedia", back_populates="event", cascade="all, delete-orphan")

# --- 4. ΠΙΝΑΚΑΣ ΠΟΛΥΜΕΣΩΝ ---
class EventMedia(Base):
    __tablename__ = 'event_media'

    id = Column(Integer, primary_key=True)
    event_id = Column(String(50), ForeignKey('events.id'))
    photo_path = Column(String(255), nullable=False)
    event = relationship("Event", back_populates="media")

# --- 5. ΠΙΝΑΚΑΣ ΤΥΠΩΝ ΕΙΣΙΤΗΡΙΩΝ ---
class TicketType(Base):
    __tablename__ = 'ticket_types'

    id = Column(String(50), primary_key=True)
    event_id = Column(String(50), ForeignKey('events.id'))
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    available = Column(Integer, nullable=False)
    event = relationship("Event", back_populates="ticket_types")
    bookings = relationship("Booking", back_populates="ticket_type")

# --- 6. ΠΙΝΑΚΑΣ ΚΡΑΤΗΣΕΩΝ ---
class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(String(50), primary_key=True)
    attendee_id = Column(Integer, ForeignKey('users.id'))
    time = Column(DateTime, default=datetime.datetime.utcnow)
    ticket_type_id = Column(String(50), ForeignKey('ticket_types.id'))
    number_of_tickets = Column(Integer, nullable=False)
    total_cost = Column(Float, nullable=False)
    booking_status = Column(String(20), default="PENDING")
    attendee = relationship("User", back_populates="bookings")
    ticket_type = relationship("TicketType", back_populates="bookings")

# --- 7. ΠΙΝΑΚΑΣ ΜΗΝΥΜΑΤΩΝ ---
class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    receiver_id = Column(Integer, ForeignKey('users.id'))
    content = Column(String(1000), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    is_read = Column(Boolean, default=False)
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="messages_received")