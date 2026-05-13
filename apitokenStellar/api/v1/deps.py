from api.v1.database import SessionLocal
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "***SECRETO_ELIMINADO_PURGA_GIT_2026-10-16***"
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
