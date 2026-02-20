from database import db
from datetime import datetime

class License(db.Model):
    __tablename__ = 'licenses'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Datos del Negocio
    business_name = db.Column(db.String(100), nullable=False)
    app_type = db.Column(db.String(50), nullable=False)
    
    # Datos del Dueño
    owner_name = db.Column(db.String(100), nullable=False)
    owner_dni = db.Column(db.String(20), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    
    # Sistema
    api_key = db.Column(db.String(100), unique=True, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    hardware_id = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Numeric(10, 2), default=0.0)

    def is_valid(self):
        return self.is_active and self.expiration_date > datetime.now()