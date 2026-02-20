from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()

# limitador de seguridad
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")