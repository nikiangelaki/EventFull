from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from datetime import datetime, timedelta, timezone
from app.database import engine, Base, get_db
from app.config import settings
from app.models import User, Message 
from app.schemas import UserCreate, Token, MessageCreate, MessageResponse 
from app.security import get_password_hash, verify_password, create_access_token, get_current_user 

from fastapi import APIRouter, Depends, HTTPException, status

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
    # Έλεγχος αν το email υπάρχει ήδη
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Το email χρησιμοποιείται ήδη.")
    
    # Κρυπτογράφηση κωδικού
    hashed_pwd = get_password_hash(user.password)
    
    # Δημιουργία χρήστη 
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
    
    # Δημιουργία JWT Token
    access_token = create_access_token(data={"sub": new_user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Σύνδεση χρήστη. Το form_data.username δέχεται το email.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Λάθος email ή κωδικός πρόσβασης.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}



@app.post("/messages/", response_model=MessageResponse)
def send_message(
    message: MessageCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user) # Παίρνουμε τον αποστολέα από το Token!
):
    # Δημιουργία του νέου μηνύματος
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


@app.get("/messages/{user_id}", response_model=list[MessageResponse])
def get_conversation(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Φέρνει τα μηνύματα όπου ο current_user είναι είτε αποστολέας είτε παραλήπτης
    # σε σχέση με τον συγκεκριμένο user_id
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