from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from sqlalchemy import or_
from typing import Optional
import uuid

from app.database import engine, Base, get_db
from app.config import settings
from app.models import User, Message, Booking, Event  
from app.schemas import UserCreate, Token, MessageCreate, MessageResponse, EventCreate, EventResponse, BookingResponse, BookingCreate
from app.security import get_password_hash, verify_password, create_access_token, get_current_user 
from app.models import Category, TicketType
from app.database import SessionLocal


def get_current_admin(current_user: User = Depends(get_current_user)):
    """
    Ελέγχει αν ο συνδεδεμένος χρήστης έχει ρόλο 'admin'.
    Αν δεν έχει, του απαγορεύει την πρόσβαση.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Δεν έχετε δικαιώματα διαχειριστή."
        )
    return current_user

# Δημιουργία όλων των tables στη βάση
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    if settings.DEBUG:
        print(f"Warning: database not available, skipping create_all: {e}", flush=True)
    else:
        raise

# Δημιουργία FastAPI app
app = FastAPI(
    title="EventFull API",
    description="API για διαχείριση εκδηλώσεων και κρατήσεων",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],
)

# --- ENDPOINTS ---

@app.get("/")
def root():
    return {
        "message": "Welcome to Eventfull API",
        "docs": "/docs", 
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.on_event("startup")
def create_default_admin():
    db = SessionLocal()
    # Ελέγχουμε αν υπάρχει ήδη ο admin
    admin = db.query(User).filter(User.username == "admin").first()
    
    if not admin:
        # Δημιουργία του προεπιλεγμένου admin
        hashed_pwd = get_password_hash("zoukizouki") 
        new_admin = User(
            username="admin",
            email="admin@eventfull.gr",
            hashed_password=hashed_pwd,
            role="admin",   
            first_name="System",
            last_name="Administrator",
            is_approved=True, # Ο admin είναι προφανώς εγκεκριμένος από την αρχή
            phone="0000000000",       
            address="System Address",  
            afm="000000000"
        )
        db.add(new_admin)
        db.commit()
        print("Ο προεπιλεγμένος διαχειριστής (admin) δημιουργήθηκε!")
        
    db.close()


# --- ADMIN ENDPOINTS ---

@app.get("/admin/users")
def get_all_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """ Επιστρέφει τη λίστα όλων των χρηστών (για πλοήγηση) """
    users = db.query(User).all()
    return users

@app.get("/admin/users/{username}")
def get_user_details(username: str, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """ Επιστρέφει τα στοιχεία ενός συγκεκριμένου χρήστη βάσει του username του """

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Ο χρήστης δεν βρέθηκε.")
    return user

@app.patch("/admin/users/{username}/approve")
def approve_user(username: str, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """ Εγκρίνει την αίτηση εγγραφής βάσει του username """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Ο χρήστης δεν βρέθηκε.")
    
    user.is_approved = True
    db.commit()
    return {"message": f"Ο χρήστης {user.username} εγκρίθηκε επιτυχώς!"}

@app.delete("/admin/users/{username}")
def reject_user(username: str, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """ Απορρίπτει (διαγράφει) την αίτηση βάσει του username """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Ο χρήστης δεν βρέθηκε.")
    
    db.delete(user)
    db.commit()
    return {"message": "Η αίτηση του χρήστη απορρίφθηκε/διαγράφηκε."}

# --- AUTHENTICATION ENDPOINTS ---

@app.post("/register", response_model=Token)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Εγγραφή νέου χρήστη.
    """
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Το email χρησιμοποιείται ήδη.")
    #PROSTHESE KAI GIA USERNAME!!!!!!!
    hashed_pwd = get_password_hash(user.password)
    
    new_user = User(
        username=user.username,
        email=user.email, 
        hashed_password=hashed_pwd,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        address=user.address,
        afm=user.afm
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Σύνδεση χρήστη με βάση το Όνομα Χρήστη (username).
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Λάθος όνομα χρήστη ή κωδικός πρόσβασης.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email}) 
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
def get_me(current_user: User = Depends(get_current_user)):
    """
    Επιστρέφει τα στοιχεία του συνδεδεμένου χρήστη.
    Το 'current_user' προέρχεται από το get_current_user που ήδη έχεις.
    """
    return current_user

# --- EVENT ENDPOINTS ---

@app.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Δημιουργία νέας εκδήλωσης, έλεγχος χωρητικότητας και αποθήκευση.
    """
    if current_user.role != "organizer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Μόνο οι Διοργανωτές μπορούν να δημιουργήσουν εκδηλώσεις."
        )
    
    # 1. ΕΛΕΓΧΟΣ ΧΩΡΗΤΙΚΟΤΗΤΑΣ (Business Rule από το DTD)
    total_requested = sum(ticket.quantity for ticket in event_data.tickets)
    if total_requested > event_data.capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Το άθροισμα των εισιτηρίων ({total_requested}) υπερβαίνει τη συνολική χωρητικότητα ({event_data.capacity})."
        )
    
    # 2. Παραγωγή μοναδικού ID
    new_event_id = f"EV-{uuid.uuid4().hex[:8].upper()}"
    
    # 3. Δημιουργία της εκδήλωσης
    new_event = Event(
        id=new_event_id,
        organizer_id=current_user.id,
        title=event_data.title,
        event_type=event_data.event_type,
        venue=event_data.venue,
        address=event_data.address,
        city=event_data.city,
        country=event_data.country,
        latitude=event_data.latitude,
        longitude=event_data.longitude,
        start_datetime=event_data.start_datetime,
        end_datetime=event_data.end_datetime,
        capacity=event_data.capacity,
        description=event_data.description,
        status="DRAFT" 
    )
    db.add(new_event)
    
    # 4. Αποθήκευση Τύπων Εισιτηρίων
    for ticket in event_data.tickets:
        new_ticket = TicketType(
            id=f"TK-{uuid.uuid4().hex[:8].upper()}",
            event_id=new_event_id,
            name=ticket.name,
            price=ticket.price,
            quantity=ticket.quantity,
            available=ticket.quantity 
        )
        db.add(new_ticket)
    
    # 5. Διαχείριση Κατηγοριών (Αν το event_data.categories είναι λίστα)
    if hasattr(event_data, 'categories') and event_data.categories:
        for cat_name in event_data.categories:
            new_cat = EventCategory(
                event_id=new_event_id,
                category_name=cat_name
            )
            db.add(new_cat)
    
    db.commit()
    db.refresh(new_event)
    
    return new_event


@app.get("/events/search")
def search_events(
    page: int = 1, 
    limit: int = 10,
    q: Optional[str] = None,          # Ελεύθερο κείμενο (Title & Description)
    category: Optional[str] = None,   # Κατηγορία
    location: Optional[str] = None,   # Τοποθεσία (Πόλη, Χώρος, Διεύθυνση)
    start_date: Optional[datetime] = None, # Χρονικό διάστημα (Από)
    end_date: Optional[datetime] = None,   # Χρονικό διάστημα (Έως)
    max_price: Optional[float] = None,     # Μέγιστη τιμή εισιτηρίου
    db: Session = Depends(get_db)
):
    """
    Προηγμένη Αναζήτηση και Φιλτράρισμα Εκδηλώσεων (Δημόσιο).
    """
    # Ξεκινάμε το query φέρνοντας ΜΟΝΟ τις Δημοσιευμένες εκδηλώσεις!
    # (Οι επισκέπτες δεν πρέπει να βλέπουν DRAFT ή CANCELLED)
    query = db.query(Event).filter(Event.status == "PUBLISHED")

    # Φίλτρο 1: Ελεύθερο Κείμενο (Ψάχνει σε Τίτλο Ή Περιγραφή)
    if q:
        search_format = f"%{q}%"
        query = query.filter(
            or_(
                Event.title.ilike(search_format),
                Event.description.ilike(search_format)
            )
        )
        
    # Φίλτρο 2: Τοποθεσία (Ψάχνει σε Πόλη Ή Χώρο Ή Διεύθυνση)
    if location:
        loc_format = f"%{location}%"
        query = query.filter(
            or_(
                Event.city.ilike(loc_format),
                Event.venue.ilike(loc_format),
                Event.address.ilike(loc_format)
            )
        )

    # Φίλτρο 3: Χρονικό Διάστημα
    if start_date:
        query = query.filter(Event.start_datetime >= start_date)
    if end_date:
        query = query.filter(Event.end_datetime <= end_date)

    # Φίλτρο 4: Κατηγορία (Κάνουμε JOIN με τον πίνακα Category)
    if category:
        query = query.join(Event.categories).filter(Category.name.ilike(f"%{category}%"))

    # Φίλτρο 5: Μέγιστη Τιμή Εισιτηρίου (Κάνουμε JOIN με τα TicketTypes)
    if max_price is not None:
        query = query.join(Event.ticket_types).filter(TicketType.price <= max_price)

    # Υπολογισμός συνολικών αποτελεσμάτων (για το Frontend)
    total_events = query.count()

    # Εφαρμογή Σελιδοποίησης (Pagination)
    skip = (page - 1) * limit
    events = query.offset(skip).limit(limit).all()

    return {
        "total": total_events,
        "page": page,
        "limit": limit,
        "events": events
    }


# --- BOOKING ENDPOINTS ---

@app.post("/events/{event_id}/book", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def book_event(
    event_id: str,
    booking_data: BookingCreate,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Πραγματοποίηση κράτησης. Υπολογίζει κόστος και μειώνει τα διαθέσιμα εισιτήρια.
    """
    # 1. Έλεγχος Ρόλου 
    if current_user.role != "attendee": 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Μόνο οι Συμμετέχοντες μπορούν να πραγματοποιήσουν κράτηση."
        )
        
    # 2. Βρίσκουμε την εκδήλωση
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Η εκδήλωση δεν βρέθηκε.")
        
    # 3. Έλεγχος αν είναι Ακυρωμένη
    if event.status == "CANCELLED":
        raise HTTPException(status_code=400, detail="Η εκδήλωση έχει ακυρωθεί. Δεν δέχεται κρατήσεις.")
        
    # 4. Βρίσκουμε το συγκεκριμένο εισιτήριο
    ticket = db.query(TicketType).filter(
        TicketType.id == booking_data.ticket_type_id,
        TicketType.event_id == event_id 
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ο τύπος εισιτηρίου δεν βρέθηκε για αυτή την εκδήλωση.")
        
    # 5. Έλεγχος Διαθεσιμότητας
    if ticket.available < booking_data.number_of_tickets:
        raise HTTPException(
            status_code=400, 
            detail=f"Δεν υπάρχουν επαρκείς διαθέσιμες θέσεις. Έχουν μείνει μόνο {ticket.available}."
        )
        
    # 6. Αφαίρεση Διαθέσιμων Θέσεων & Υπολογισμός Κόστους
    ticket.available -= booking_data.number_of_tickets 
    total_cost = ticket.price * booking_data.number_of_tickets
    
    # 7. Δημιουργία της Κράτησης
    new_booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"
    new_booking = Booking(
        id=new_booking_id,
        attendee_id=current_user.id, # Στο μοντέλο σου το είπες attendee_id αντί για user_id
        event_id=event_id,
        ticket_type_id=ticket.id,
        number_of_tickets=booking_data.number_of_tickets,
        total_cost=total_cost,
        booking_status="CONFIRMED"
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return new_booking


# --- ORGANIZER EVENT MANAGEMENT ENDPOINTS ---

@app.patch("/events/{event_id}/publish")
def publish_event(
    event_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Δημοσίευση Εκδήλωσης (Αλλαγή από DRAFT σε PUBLISHED)
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Η εκδήλωση δεν βρέθηκε.")
        
    # Έλεγχος ότι αυτός που πάει να τη δημοσιεύσει είναι όντως ο δημιουργός της
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Μόνο ο διοργανωτής της εκδήλωσης μπορεί να τη δημοσιεύσει.")
        
    event.status = "PUBLISHED"
    db.commit()
    
    return {"message": "Η εκδήλωση δημοσιεύτηκε επιτυχώς!"}


@app.patch("/events/{event_id}/cancel")
def cancel_event(
    event_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Ακύρωση Εκδήλωσης (Αλλαγή σε CANCELLED)
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Η εκδήλωση δεν βρέθηκε.")
        
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Δεν έχετε δικαίωμα ακύρωσης αυτής της εκδήλωσης.")
        
    event.status = "CANCELLED"
    db.commit()
    
    # --- ΕΝΣΩΜΑΤΩΣΗ ΜΗΝΥΜΑΤΩΝ (Που είχες φτιάξει παλαιότερα) ---
    bookings = db.query(Booking).filter(Booking.event_id == event_id).all()
    for booking in bookings:
        cancel_msg = Message(
            sender_id=current_user.id,
            receiver_id=booking.attendee_id,
            event_id=event_id,
            content=f"Σας ενημερώνουμε ότι η εκδήλωση '{event.title}' ακυρώθηκε."
        )
        db.add(cancel_msg)
    db.commit()
    
    return {"message": "Η εκδήλωση ακυρώθηκε και οι συμμετέχοντες ενημερώθηκαν με μήνυμα."}


@app.delete("/events/{event_id}")
def delete_event(
    event_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Διαγραφή Εκδήλωσης (Επιτρέπεται ΜΟΝΟ αν δεν υπάρχουν κρατήσεις)
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Η εκδήλωση δεν βρέθηκε.")
        
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Δεν έχετε δικαίωμα διαγραφής.")
        
    # ΕΛΕΓΧΟΣ ΕΚΦΩΝΗΣΗΣ: Διαγραφή επιτρέπεται ΜΟΝΟ πριν την πρώτη κράτηση!
    has_bookings = db.query(Booking).filter(Booking.event_id == event_id).first()
    if has_bookings:
        raise HTTPException(
            status_code=400, 
            detail="Δεν μπορείτε να διαγράψετε την εκδήλωση γιατί υπάρχουν ήδη κρατήσεις. Δοκιμάστε να την ακυρώσετε."
        )
        
    db.delete(event)
    db.commit()
    
    return {"message": "Η εκδήλωση διαγράφηκε επιτυχώς."}

@app.put("/events/{event_id}", response_model=EventResponse)
def update_event(
    event_id: str,
    event_data: EventCreate, # Χρησιμοποιούμε το ίδιο Schema που έχουμε για τη δημιουργία
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
   Μεταβολή στοιχείων εκδήλωσης. 
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Η εκδήλωση δεν βρέθηκε.")
        
    # Έλεγχος ότι ανήκει σε αυτόν τον διοργανωτή
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Δεν έχετε δικαίωμα επεξεργασίας αυτής της εκδήλωσης.")
        
    # Ενημέρωση των βασικών στοιχείων στη βάση δεδομένων
    event.title = event_data.title
    event.event_type = event_data.event_type
    event.venue = event_data.venue
    event.address = event_data.address
    event.city = event_data.city
    event.country = event_data.country
    event.latitude = event_data.latitude
    event.longitude = event_data.longitude
    event.start_datetime = event_data.start_datetime
    event.end_datetime = event_data.end_datetime
    event.capacity = event_data.capacity
    event.description = event_data.description
    
    # Αποθήκευση αλλαγών
    db.commit()
    db.refresh(event)
    
    return event


@app.get("/organizer/events")
def get_organizer_events_with_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Επιστροφή όλων των εκδηλώσεων του συνδεδεμένου διοργανωτή,
    μαζί με όλες τις κρατήσεις που έχουν γίνει για καθεμία από αυτές.
    """
    if current_user.role != "organizer":
        raise HTTPException(status_code=403, detail="Μόνο οι διοργανωτές έχουν πρόσβαση σε αυτή τη λίστα.")
        
    # 1. Βρίσκουμε ΟΛΕΣ τις εκδηλώσεις που έχει φτιάξει αυτός ο χρήστης
    my_events = db.query(Event).filter(Event.organizer_id == current_user.id).all()
    
    # 2. Φτιάχνουμε μια λίστα που θα τα περιέχει όλα νοικοκυρεμένα για το Frontend
    result = []
    
    for event in my_events:
        # Ψάχνουμε τις κρατήσεις ΜΟΝΟ για το συγκεκριμένο event
        event_bookings = db.query(Booking).filter(Booking.event_id == event.id).all()
        
        # Πακετάρουμε τα δεδομένα
        result.append({
            "event_id": event.id,
            "title": event.title,
            "status": event.status,
            "capacity": event.capacity,
            "total_bookings_count": len(event_bookings),
            "bookings_list": event_bookings # Το FastAPI θα μετατρέψει αυτόματα τη λίστα σε JSON
        })
        
    return result




# --- MESSAGING ENDPOINTS ---

@app.post("/messages/", response_model=MessageResponse)
def send_message(
    message: MessageCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    new_message = Message(
        sender_id=current_user.id,
        receiver_id=message.receiver_id,
        event_id=message.event_id,
        content=message.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


# ΔΙΟΡΘΩΣΗ 2: Μετακινήσαμε τα σταθερά URLs ΠΡΙΝ από το {user_id}

@app.get("/messages/inbox", response_model=list[MessageResponse])
def get_inbox(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Φέρνει όλα τα μηνύματα που έχουν σταλεί στον τρέχοντα χρήστη """
    return db.query(Message).filter(Message.receiver_id == current_user.id).order_by(Message.timestamp.desc()).all()


@app.get("/messages/sent", response_model=list[MessageResponse])
def get_sent_messages(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Φέρνει όλα τα μηνύματα που έχει στείλει ο τρέχων χρήστης """
    return db.query(Message).filter(Message.sender_id == current_user.id).order_by(Message.timestamp.desc()).all()


@app.get("/messages/unread-count")
def get_unread_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Επιστρέφει τον αριθμό των αδιάβαστων μηνυμάτων """
    count = db.query(Message).filter(
        Message.receiver_id == current_user.id, 
        Message.is_read == False
    ).count()
    return {"unread_count": count}


@app.get("/messages/{user_id}", response_model=list[MessageResponse])
def get_conversation(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """ Φέρνει τη συνομιλία (chat) με έναν συγκεκριμένο χρήστη """
    messages = db.query(Message).filter(
        (
            (Message.sender_id == current_user.id) & (Message.receiver_id == user_id)
        ) | (
            (Message.sender_id == user_id) & (Message.receiver_id == current_user.id)
        )
    ).order_by(Message.timestamp.asc()).all()
    
    if not messages:
        raise HTTPException(status_code=404, detail="Δεν βρέθηκαν μηνύματα.")
        
    return messages


@app.delete("/messages/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Το μήνυμα δεν βρέθηκε.")
    
    if msg.sender_id != current_user.id and msg.receiver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Δεν έχετε δικαίωμα διαγραφής.")
        
    db.delete(msg)
    db.commit()
    return {"message": "Το μήνυμα διαγράφηκε επιτυχώς"}


