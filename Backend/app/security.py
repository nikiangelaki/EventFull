from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User

# Διαμόρφωση του context κρυπτογράφησης με χρήση του αλγορίθμου bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Σταθερές για τη διαχείριση των JSON Web Tokens (JWT)
ALGORITHM = "HS256"

# Καθορισμός του URL για την ανάκτηση του token (χρησιμοποιείται από το Swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Επαληθεύει εάν το δοθέν απλό κείμενο κωδικού αντιστοιχεί στο αποθηκευμένο hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Παράγει και επιστρέφει το ασφαλές hash ενός κωδικού πρόσβασης.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Δημιουργεί ένα νέο JWT access token. 
    Ενσωματώνει τα δεδομένα του χρήστη και την ημερομηνία λήξης.
    """
    to_encode = data.copy()
    
    # Υπολογισμός του χρόνου λήξης του token
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Κρυπτογράφηση και δημιουργία του τελικού token
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Επαληθεύει την εγκυρότητα του JWT token και ανακτά τον αντίστοιχο χρήστη
    από τη βάση δεδομένων. Εγείρει HTTP 401 σε περίπτωση σφάλματος ταυτοποίησης.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Αποτυχία επαλήθευσης διαπιστευτηρίων",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Αποκωδικοποίηση του token και εξαγωγή του payload
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
            
    except Exception:
        # Χειρισμός περιπτώσεων ληγμένου ή αλλοιωμένου token
        raise credentials_exception

    # Αναζήτηση της εγγραφής του χρήστη στη βάση δεδομένων
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
        
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Ελέγχει εάν ο πιστοποιημένος χρήστης διαθέτει δικαιώματα διαχειριστή (Admin).
    Εγείρει HTTP 403 εάν ο χρήστης δεν έχει τον κατάλληλο ρόλο.
    """
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ανεπαρκή δικαιώματα πρόσβασης."
        )
        
    return current_user