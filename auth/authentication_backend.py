from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from settings import get_settings

settings= get_settings()
SECRET = settings.auth

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)