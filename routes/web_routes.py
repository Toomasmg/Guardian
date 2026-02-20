from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_user, login_required, logout_user, current_user
from database import db
# IMPORTANTE: Agregamos Category aquí abajo
from models import AdminUser, License, Category
from datetime import datetime, timedelta
from sqlalchemy import or_
import uuid
import csv
import io

web_bp = Blueprint('web', __name__)
REGISTRATION_CODE = "MASTER123"

# --- NUEVA RUTA: CREAR CATEGORÍA ---
@web_bp.route('/add_category', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('category_name')
    if name:
        # Verificar que no exista
        exists = Category.query.filter_by(name=name).first()
        if not exists:
            new_cat = Category(name=name)
            db.session.add(new_cat)
            db.session.commit()
            flash(f'Rubro "{name}" agregado exitosamente.')
        else:
            flash('Ese rubro ya existe.')
    return redirect(url_for('web.dashboard'))

# --- RUTA DASHBOARD ACTUALIZADA ---
@web_bp.route('/')
@login_required
def dashboard():
    search_query = request.args.get('q')
    status_filter = request.args.get('status')
    
    query = License.query
    now = datetime.now()

    if search_query:
        term = f"%{search_query}%"
        query = query.filter(or_(
            License.business_name.ilike(term), 
            License.owner_dni.ilike(term)
        ))
    
    if status_filter == 'active':
        query = query.filter(License.is_active == True, License.expiration_date > now)
    elif status_filter == 'expired':
        query = query.filter(or_(License.is_active == False, License.expiration_date <= now))

    licenses = query.order_by(License.expiration_date.asc()).all()
    
    # NUEVO: Cargamos las categorías para enviarlas al HTML
    categories = Category.query.order_by(Category.name.asc()).all()
    
    # Estadísticas
    all_lics = License.query.all()
    active_count = sum(1 for l in all_lics if l.is_active and l.expiration_date > now)
    revenue = sum(float(l.price) for l in all_lics if l.is_active)
    
    app_types = {}
    for l in all_lics:
        app_types[l.app_type] = app_types.get(l.app_type, 0) + 1

    stats = {
        "total": len(all_lics), 
        "active": active_count, 
        "expired": len(all_lics) - active_count,
        "revenue": revenue, 
        "chart_labels": list(app_types.keys()), 
        "chart_values": list(app_types.values())
    }
    
    # Pasamos 'categories' al render_template
    return render_template('dashboard.html', licenses=licenses, categories=categories, now=now, search_query=search_query, status_filter=status_filter, stats=stats)

# --- (EL RESTO DEL ARCHIVO SIGUE IGUAL ABAJO...) ---
# Copia aquí el resto de tus rutas (login, register, create_license, etc.)
# Solo asegúrate de que 'create_license' reciba el app_type del form como siempre.

# --- EXPORTAR EXCEL ---
@web_bp.route('/export_data')
@login_required
def export_data():
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    
    writer.writerow(['ID', 'Negocio', 'Dueño', 'DNI', 'Estado', 'Vencimiento', 'Precio', 'API Key', 'HWID Vinculado'])
    
    for lic in License.query.order_by(License.expiration_date.asc()).all():
        estado = "ACTIVO" if lic.is_active and lic.expiration_date > datetime.now() else "INACTIVO"
        hwid_status = "SI" if lic.hardware_id else "NO"
        
        writer.writerow([
            lic.id, lic.business_name, lic.owner_name, lic.owner_dni,
            estado, lic.expiration_date.strftime('%d/%m/%Y'),
            f"${lic.price:.2f}", lic.api_key, hwid_status
        ])
        
    output.seek(0)
    return Response(
        output.getvalue().encode('utf-8-sig'),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=reporte_clientes.csv"}
    )

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('web.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = AdminUser.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('web.dashboard'))
        
        flash('Usuario o contraseña incorrectos.')
    return render_template('login.html')

@web_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.form.get('secret_code') != REGISTRATION_CODE: 
            flash('Código de seguridad incorrecto.')
            return render_template('register.html')
            
        if AdminUser.query.filter_by(username=request.form.get('username')).first(): 
            flash('El usuario ya existe.')
            return render_template('register.html')
            
        new_admin = AdminUser(
            username=request.form.get('username'),
            phone=request.form.get('phone'),
            recovery_pin=request.form.get('recovery_pin'),
            dni=request.form.get('dni')
        )
        new_admin.set_password(request.form.get('password'))
        
        db.session.add(new_admin)
        db.session.commit()
        flash('Cuenta creada con éxito.')
        return redirect(url_for('web.login'))
    return render_template('register.html')

@web_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        user = AdminUser.query.filter_by(username=request.form.get('username')).first()
        if user and user.recovery_pin == request.form.get('pin'):
            user.set_password(request.form.get('new_password'))
            db.session.commit()
            flash('Contraseña restablecida.')
            return redirect(url_for('web.login'))
        flash('Datos incorrectos.')
    return render_template('reset_password.html')

@web_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('web.login'))

@web_bp.route('/create_license', methods=['POST'])
@login_required
def create_license():
    try:
        new_license = License(
            business_name=request.form.get('business_name'),
            app_type=request.form.get('app_type'),
            owner_name=request.form.get('owner_name'),
            owner_dni=request.form.get('owner_dni'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            api_key=str(uuid.uuid4()),
            expiration_date=datetime.now() + timedelta(days=int(request.form.get('days', 30))),
            price=float(request.form.get('price', 0.0))
        )
        db.session.add(new_license)
        db.session.commit()
        flash('Licencia creada correctamente.')
    except Exception as e:
        flash(f'Error al crear: {str(e)}')
    return redirect(url_for('web.dashboard'))

@web_bp.route('/renew/<int:id>', methods=['POST'])
@login_required
def renew(id):
    l = db.session.get(License, id)
    if l:
        if l.expiration_date < datetime.now():
            l.expiration_date = datetime.now() + timedelta(days=30)
        else:
            l.expiration_date += timedelta(days=30)
        l.is_active = True
        db.session.commit()
        flash(f'Renovada: {l.business_name}')
    return redirect(url_for('web.dashboard'))

@web_bp.route('/modify_days/<int:id>', methods=['POST'])
@login_required
def modify_days(id):
    l = db.session.get(License, id)
    try:
        days = int(request.form.get('days', 0))
        if l:
            if days > 0 and l.expiration_date < datetime.now():
                l.expiration_date = datetime.now() + timedelta(days=days)
            else:
                l.expiration_date += timedelta(days=days)
            l.is_active = True
            db.session.commit()
            flash('Días modificados.')
    except ValueError:
        flash('Valor inválido.')
    return redirect(url_for('web.dashboard'))

@web_bp.route('/toggle/<int:id>', methods=['POST'])
@login_required
def toggle(id):
    l = db.session.get(License, id)
    if l:
        l.is_active = not l.is_active
        db.session.commit()
        flash(f'Estado cambiado para {l.business_name}.')
    return redirect(url_for('web.dashboard'))

@web_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    l = db.session.get(License, id)
    if l:
        db.session.delete(l)
        db.session.commit()
        flash('Licencia eliminada.')
    return redirect(url_for('web.dashboard'))

@web_bp.route('/reset_hwid/<int:id>', methods=['POST'])
@login_required
def reset_hwid(id):
    l = db.session.get(License, id)
    if l:
        l.hardware_id = None
        db.session.commit()
        flash('Dispositivo desvinculado. Ahora puede usarse en otra PC.')
    return redirect(url_for('web.dashboard'))