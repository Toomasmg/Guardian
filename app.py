import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_login import LoginManager
from database import db, limiter
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()

base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')

if not all([db_user, db_host, db_name]):
    print("❌ ERROR: Faltan variables en .env")
    sys.exit(1)

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'clave_dev'

db.init_app(app)
limiter.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'web.login'
login_manager.login_message_category = "info"

from models import AdminUser, License, Category
from routes.web_routes import web_bp
from routes.api_routes import api_bp

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(AdminUser, int(user_id))

app.register_blueprint(web_bp)
app.register_blueprint(api_bp)

if not app.debug:
    file_handler = RotatingFileHandler('sistema.log', maxBytes=102400, backupCount=10, encoding='utf-8')
    
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [en %(pathname)s:%(lineno)d]'
    ))
    
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("✅ Base de Datos conectada.")
            
            if not AdminUser.query.filter_by(username='admin').first():
                admin = AdminUser(username='admin', dni='0000', phone='000', recovery_pin='0000')
                admin.set_password('admin')
                db.session.add(admin)
                db.session.commit()                
        except Exception as e:
            app.logger.critical(f"❌ Error DB: {e}")
            print(f"❌ Error Fatal: {e}")
    
    print("🚀 Servidor corriendo (Logs activados en 'sistema.log')")
    app.run(debug=True, port=5000, use_reloader=False)