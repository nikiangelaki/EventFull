from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from app.config import settings

# Ορίζουμε τον αλγόριθμο κρυπτογράφησης κωδικών (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Ορίζουμε τον αλγόριθμο για τα JWT (είναι το παγκόσμιο στάνταρ)
ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Παίρνει τον κωδικό που έγραψε ο χρήστης στο Login (plain)
    και τον συγκρίνει με τον κρυπτογραφημένο που έχουμε στη βάση (hashed).
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Παίρνει έναν απλό κωδικό (π.χ. 'maria123') και επιστρέφει
    την κρυπτογραφημένη του μορφή για να μπει στη βάση.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Δημιουργεί το JWT Token (Το 'βραχιολάκι' εισόδου).
    """
    to_encode = data.copy()
    
    # Υπολογισμός πότε θα λήξει το token
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Αν δεν ορίσουμε χρόνο, παίρνει το προεπιλεγμένο από το .env
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Προσθέτουμε την ημερομηνία λήξης (exp) στα δεδομένα του token
    to_encode.update({"exp": expire})
    
    # Υπογραφή του token με το SECRET_KEY μας από το .env!
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt