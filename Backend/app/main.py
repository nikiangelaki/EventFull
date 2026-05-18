from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.database import engine, Base, get_db
from app.config import settings
# ΔΙΟΡΘΩΣΗ 1: Προσθήκη του Booking στα imports (υποθέτοντας ότι το μοντέλο σου λέγεται Booking)
from app.models import User, Message, Booking 
from app.schemas import UserCreate, Token, MessageCreate, MessageResponse 
from app.security import get_password_hash, verify_password, create_access_token, get_current_user 

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


# --- AUTHENTICATION ENDPOINTS ---

@app.post("/register", response_model=Token)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Εγγραφή νέου χρήστη.
    """
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Το email χρησιμοποιείται ήδη.")
    
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


# --- EVENT CANCELLATION ENDPOINT ---

@app.post("/events/{event_id}/cancel")
def cancel_event_and_notify(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. Βρες όλους όσους έχουν κάνει κράτηση για τη συγκεκριμένη εκδήλωση
    bookings = db.query(Booking).filter(Booking.event_id == event_id).all()
    
    # 2. Στείλε αυτόματα ενημερωτικό μήνυμα σε όλους
    for booking in bookings:
        cancel_msg = Message(
            sender_id=current_user.id, 
            receiver_id=booking.user_id, 
            event_id=event_id,
            content=f"Σας ενημερώνουμε ότι η εκδήλωση ακυρώθηκε."
        )
        db.add(cancel_msg)
    
    db.commit()
    return {"message": "Η εκδήλωση ακυρώθηκε και εστάλησαν τα μηνύματα ενημέρωσης."}