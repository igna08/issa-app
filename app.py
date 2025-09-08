from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_wtf import CSRFProtect, FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Optional
import datetime
import mercadopago
from functools import wraps
import os

app = Flask(__name__)
# Absolute path for DB to avoid ambiguity
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'school.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{db_path}')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a-very-secret-key-for-dev')
app.config['MERCADOPAGO_ACCESS_TOKEN'] = os.getenv('MERCADOPAGO_ACCESS_TOKEN')

# Email Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
csrf = CSRFProtect(app)
sdk = mercadopago.SDK(app.config['MERCADOPAGO_ACCESS_TOKEN'])

# Models...
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(50), nullable=False)
    wit = db.Column(db.String(100), nullable=True)
    tipo_inscripcion = db.Column(db.String(50), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    estado_pago = db.Column(db.String(50), default='Pendiente', nullable=False)
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    curso = db.relationship('Curso', backref=db.backref('usuarios', lazy=True))

class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    cupo_maximo = db.Column(db.Integer, nullable=True)
    fecha_inicio = db.Column(db.Date, nullable=True)
    fecha_fin = db.Column(db.Date, nullable=True)

class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    estado_pago = db.Column(db.String(50), nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    referencia = db.Column(db.String(100), nullable=False)

class Notificacion(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo = db.Column(db.String(50), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    leida = db.Column(db.Boolean, default=False, nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('notificaciones', lazy=True))

class Administrador(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Forms
class InscriptionForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido = StringField('Apellido', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telefono = StringField('Teléfono', validators=[DataRequired()])
    wit = StringField('WIT', validators=[Optional()])
    tipo_inscripcion = SelectField('Tipo de inscripción', choices=[('profesorado', 'Profesorado'), ('secundario', 'Secundario'), ('otros', 'Otros')], validators=[DataRequired()])
    curso_id = SelectField('Carrera específica', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Proceder al Pago')

class AdminLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CourseForm(FlaskForm):
    tipo = SelectField('Tipo', choices=[('profesorado', 'Profesorado'), ('secundario', 'Secundario'), ('otros', 'Otros')], validators=[DataRequired()])
    nombre = StringField('Nombre', validators=[DataRequired()])
    precio = StringField('Precio', validators=[DataRequired()])
    cupo_maximo = StringField('Cupo Máximo', validators=[Optional()])
    fecha_inicio = StringField('Fecha de Inicio', validators=[Optional()])
    fecha_fin = StringField('Fecha de Fin', validators=[Optional()])
    submit = SubmitField('Save')


# Decorator for admin routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Email function...
def send_email(to, subject, template):
    msg = Message(subject, recipients=[to], html=template, sender=app.config['MAIL_DEFAULT_SENDER'])
    mail.send(msg)

# Public routes...
@app.route('/')
def home():
    courses = Curso.query.order_by(Curso.nombre).all()
    return render_template('home.html', courses=courses)

@app.route('/inscripcion', methods=['GET', 'POST'])
def inscripcion():
    form = InscriptionForm()
    form.curso_id.choices = [(c.id, c.nombre) for c in Curso.query.order_by('nombre').all()]

    if request.method == 'GET':
        course_id = request.args.get('course_id', type=int)
        if course_id:
            # Check if course exists
            course = Curso.query.get(course_id)
            if course:
                form.curso_id.data = course_id
                form.tipo_inscripcion.data = course.tipo

    if form.validate_on_submit():
        # ... (form processing logic)
        new_user = Usuario(
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            email=form.email.data,
            telefono=form.telefono.data,
            wit=form.wit.data,
            tipo_inscripcion=form.tipo_inscripcion.data,
            curso_id=form.curso_id.data
        )
        db.session.add(new_user)
        db.session.commit()

        curso = Curso.query.get(form.curso_id.data)
        # Create payment preference
        preference_data = {
            "items": [{"title": curso.nombre, "quantity": 1, "unit_price": float(curso.precio)}],
            "payer": {"name": form.nombre.data, "surname": form.apellido.data, "email": form.email.data},
            "back_urls": {
                "success": url_for('payment_success', _external=True),
                "failure": url_for('payment_failure', _external=True),
                "pending": url_for('payment_pending', _external=True)
            },
            "auto_return": "approved",
            "external_reference": str(new_user.id),
            "notification_url": url_for('payment_webhook', _external=True)
        }
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        return redirect(preference["init_point"])

    return render_template('inscription.html', form=form)

# ... (payment routes)
@app.route('/inscripcion/pago', methods=['POST'])
@csrf.exempt
def payment_webhook():
    # ... (webhook logic)
    data = request.get_json()
    if data and data.get('type') == 'payment':
        payment_id = data['data']['id']
        payment_info = sdk.payment().get(payment_id)
        payment = payment_info['response']

        if payment['status'] == 'approved':
            user_id = payment['external_reference']
            user = Usuario.query.get(user_id)
            if user and user.estado_pago != 'Pagado':
                user.estado_pago = 'Pagado'
                new_pago = Pago(usuario_id=user.id, curso_id=user.curso_id, estado_pago='Pagado', referencia=payment_id)
                db.session.add(new_pago)

                # Create notification for admin panel
                new_notification = Notificacion(tipo='Nueva Inscripción', usuario_id=user.id)
                db.session.add(new_notification)

                db.session.commit()

                # Send emails
                user_subject = "Inscripción confirmada"
                user_html = f"<p>Hola {user.nombre},</p><p>Tu inscripción al curso {user.curso.nombre} ha sido confirmada.</p>"
                send_email(user.email, user_subject, user_html)
                school_subject = f"Nueva inscripción: {user.nombre} {user.apellido}"
                school_html = f"<p>Se ha registrado una nueva inscripción para el curso {user.curso.nombre}.</p><p>Usuario: {user.nombre} {user.apellido} ({user.email})</p>"
                send_email(app.config['MAIL_USERNAME'], school_subject, school_html)
    return jsonify({'status': 'ok'}), 200

@app.route('/payment/success')
def payment_success(): return "Payment successful!"
@app.route('/payment/failure')
def payment_failure(): return "Payment failed."
@app.route('/payment/pending')
def payment_pending(): return "Payment pending."
@app.route('/api/courses/<type>')
def api_courses(type):
    courses = Curso.query.filter_by(tipo=type).all()
    return jsonify([{'id': c.id, 'name': c.nombre, 'price': float(c.precio)} for c in courses])

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = Administrador.query.filter_by(email=form.email.data).first()
        if admin and bcrypt.check_password_hash(admin.password, form.password.data):
            session['admin_id'] = admin.id
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('admin/login.html', form=form)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    users = Usuario.query.order_by(Usuario.fecha_inscripcion.desc()).all()
    courses = Curso.query.all()
    notifications = Notificacion.query.order_by(Notificacion.fecha.desc()).all()
    return render_template('admin/dashboard.html', users=users, courses=courses, notifications=notifications, title="Dashboard")

@app.route('/admin/courses')
@admin_required
def admin_courses():
    courses = Curso.query.order_by(Curso.nombre).all()
    return render_template('admin/courses.html', courses=courses, title="Gestionar Cursos")

@app.route('/admin/users')
@admin_required
def admin_users():
    users = Usuario.query.order_by(Usuario.fecha_inscripcion.desc()).all()
    return render_template('admin/users.html', users=users, title="Usuarios Inscritos")

# Course management
@app.route('/admin/course/add', methods=['GET', 'POST'])
@admin_required
def add_course():
    form = CourseForm()
    if form.validate_on_submit():
        new_course = Curso(
            tipo=form.tipo.data,
            nombre=form.nombre.data,
            precio=form.precio.data,
            cupo_maximo=int(form.cupo_maximo.data) if form.cupo_maximo.data else None,
            fecha_inicio=datetime.datetime.strptime(form.fecha_inicio.data, '%Y-%m-%d').date() if form.fecha_inicio.data else None,
            fecha_fin=datetime.datetime.strptime(form.fecha_fin.data, '%Y-%m-%d').date() if form.fecha_fin.data else None
        )
        db.session.add(new_course)
        db.session.commit()
        flash('Course added successfully.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/course_form.html', title='Add Course', form=form)

@app.route('/admin/course/edit/<int:course_id>', methods=['GET', 'POST'])
@admin_required
def edit_course(course_id):
    course = Curso.query.get_or_404(course_id)
    form = CourseForm(obj=course)
    if form.validate_on_submit():
        course.tipo = form.tipo.data
        course.nombre = form.nombre.data
        course.precio = form.precio.data
        course.cupo_maximo = int(form.cupo_maximo.data) if form.cupo_maximo.data else None
        course.fecha_inicio = datetime.datetime.strptime(form.fecha_inicio.data, '%Y-%m-%d').date() if form.fecha_inicio.data else None
        course.fecha_fin = datetime.datetime.strptime(form.fecha_fin.data, '%Y-%m-%d').date() if form.fecha_fin.data else None
        db.session.commit()
        flash('Course updated successfully.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/course_form.html', title='Edit Course', form=form, course=course)

@app.route('/admin/course/delete/<int:course_id>', methods=['POST'])
@admin_required
def delete_course(course_id):
    course = Curso.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully.', 'danger')
    return redirect(url_for('admin_courses'))

# Context processor to inject notifications into all admin templates
@app.context_processor
def inject_notifications():
    if 'admin_id' in session:
        unread_count = Notificacion.query.filter_by(leida=False).count()
        # Fetch last 5 notifications for the dropdown
        recent_notifications = Notificacion.query.order_by(Notificacion.fecha.desc()).limit(5).all()
        return dict(unread_notifications_count=unread_count, recent_notifications=recent_notifications)
    return dict()

@app.route('/admin/notification/mark-read/<int:notification_id>')
@admin_required
def mark_notification_read(notification_id):
    notification = Notificacion.query.get_or_404(notification_id)
    notification.leida = True
    db.session.commit()
    # Redirect to the main users page, where the admin can see the user who enrolled
    flash(f"Notificación marcada como leída.", "success")
    return redirect(url_for('admin_users'))

if __name__ == '__main__':
    app.run(debug=True)
