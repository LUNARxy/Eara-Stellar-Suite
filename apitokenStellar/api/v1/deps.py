from config import JWT_SECRET_KEY
from api.v1.database import SessionLocal
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_MINUTES = 180

_reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/v1/public/login/access_token"
)


# Dependency
def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
