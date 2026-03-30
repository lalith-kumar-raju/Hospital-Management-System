import sqlite3
import os
from datetime import datetime
from functools import wraps
from flask import (Flask, render_template, request, redirect, url_for,
                   session, flash, jsonify, g)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'hospital_secret_key_2026'

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hospital.db')

#  Database Helper 

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

#  Create Tables 

def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute("PRAGMA foreign_keys = ON")
    cur = db.cursor()

    cur.executescript('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS specializations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            specialization_id INTEGER,
            qualification TEXT,
            experience INTEGER DEFAULT 0,
            bio TEXT,
            is_available INTEGER DEFAULT 1,
            FOREIGN KEY (specialization_id) REFERENCES specializations(id)
        );
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT DEFAULT 'bi-heart-pulse',
            is_active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            gender TEXT,
            blood_group TEXT,
            dob TEXT,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_no TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            time_slot TEXT NOT NULL,
            booking_type TEXT DEFAULT 'doctor',
            disease TEXT,
            symptoms TEXT,
            prescription TEXT,
            status TEXT DEFAULT 'Scheduled',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        );
    ''')
    db.commit()
    db.close()

#  Disease to Specialization Mapping 

DISEASE_SPEC_MAP = {
    'Fever': 'General Medicine',
    'Cold & Flu': 'General Medicine',
    'Headache': 'Neurology',
    'Migraine': 'Neurology',
    'Chest Pain': 'Cardiology',
    'Heart Palpitations': 'Cardiology',
    'Skin Rash': 'Dermatology',
    'Acne': 'Dermatology',
    'Back Pain': 'Orthopedics',
    'Fracture': 'Orthopedics',
    'Child Illness': 'Pediatrics',
    'Eye Problem': 'Ophthalmology',
    'Ear Infection': 'ENT',
    'Sore Throat': 'ENT',
    'Diabetes': 'Endocrinology',
    'Thyroid Issue': 'Endocrinology',
    'Anxiety': 'Psychiatry',
    'Depression': 'Psychiatry',
    'Pregnancy Care': 'Gynecology',
    'Menstrual Issues': 'Gynecology',
}

TIME_SLOTS = [
    '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM',
    '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM',
    '02:00 PM', '02:30 PM', '03:00 PM', '03:30 PM',
    '04:00 PM', '04:30 PM', '05:00 PM'
]

#  Auth Decorators 

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin login required.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

def doctor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'doctor_id' not in session:
            flash('Doctor login required.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

#  Context Processor 

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

#  USER ROUTES

@app.route('/')
def home():
    db = get_db()
    services = db.execute("SELECT * FROM services WHERE is_active=1 LIMIT 4").fetchall()
    doctors = db.execute("""
        SELECT d.*, s.name as specialization
        FROM doctors d JOIN specializations s ON d.specialization_id = s.id
        WHERE d.is_available = 1 LIMIT 4
    """).fetchall()
    total_doctors = db.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
    total_patients = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_services = db.execute("SELECT COUNT(*) FROM services WHERE is_active=1").fetchone()[0]
    return render_template('index.html', services=services, doctors=doctors,
                           total_doctors=total_doctors, total_patients=total_patients,
                           total_services=total_services)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form['gender']
        blood_group = request.form['blood_group']
        dob = request.form['dob']
        password = request.form['password']

        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE email=? OR phone=?", (email, phone)).fetchone()
        if existing:
            flash('Email or Phone already registered. Please login.', 'danger')
            return redirect(url_for('register'))

        db.execute("""INSERT INTO users (full_name, email, phone, gender, blood_group, dob, password_hash)
                      VALUES (?, ?, ?, ?, ?, ?, ?)""",
                   (full_name, email, phone, gender, blood_group, dob, generate_password_hash(password)))
        db.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            flash('Welcome back, ' + user['full_name'] + '!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    uid = session['user_id']
    total = db.execute("SELECT COUNT(*) FROM appointments WHERE user_id=?", (uid,)).fetchone()[0]
    scheduled = db.execute("SELECT COUNT(*) FROM appointments WHERE user_id=? AND status='Scheduled'", (uid,)).fetchone()[0]
    completed = db.execute("SELECT COUNT(*) FROM appointments WHERE user_id=? AND status='Completed'", (uid,)).fetchone()[0]
    cancelled = db.execute("SELECT COUNT(*) FROM appointments WHERE user_id=? AND status='Cancelled'", (uid,)).fetchone()[0]
    upcoming = db.execute("""
        SELECT a.*, d.full_name as doctor_name, s.name as specialization
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        JOIN specializations s ON d.specialization_id = s.id
        WHERE a.user_id=? AND a.status='Scheduled'
        ORDER BY a.appointment_date, a.time_slot
    """, (uid,)).fetchall()
    return render_template('dashboard.html', total=total, scheduled=scheduled,
                           completed=completed, cancelled=cancelled, upcoming=upcoming)

@app.route('/services')
def services():
    db = get_db()
    all_services = db.execute("SELECT * FROM services WHERE is_active=1").fetchall()
    return render_template('services.html', services=all_services)

@app.route('/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    db = get_db()
    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        date = request.form['appointment_date']
        slot = request.form['time_slot']
        symptoms = request.form.get('symptoms', '')

        # Check slot conflict
        conflict = db.execute("""SELECT id FROM appointments
            WHERE doctor_id=? AND appointment_date=? AND time_slot=? AND status != 'Cancelled'""",
            (doctor_id, date, slot)).fetchone()
        if conflict:
            flash('This time slot is already booked. Please choose another.', 'danger')
            return redirect(url_for('book_appointment'))

        doctor = db.execute("SELECT full_name FROM doctors WHERE id=?", (doctor_id,)).fetchone()
        receipt_no = 'HMS' + datetime.now().strftime('%Y%m%d%H%M%S')
        db.execute("""INSERT INTO appointments (receipt_no, user_id, doctor_id, appointment_date,
                      time_slot, booking_type, symptoms, status)
                      VALUES (?, ?, ?, ?, ?, 'Doctor', ?, 'Scheduled')""",
                   (receipt_no, session['user_id'], doctor_id, date, slot, symptoms))
        db.commit()
        apt = db.execute("SELECT id FROM appointments WHERE receipt_no=?", (receipt_no,)).fetchone()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('receipt', apt_id=apt['id']))

    doctors = db.execute("""
        SELECT d.*, s.name as specialization
        FROM doctors d JOIN specializations s ON d.specialization_id = s.id
        WHERE d.is_available = 1 ORDER BY d.full_name
    """).fetchall()
    return render_template('book_appointment.html', doctors=doctors, time_slots=TIME_SLOTS)

@app.route('/book-by-disease', methods=['GET', 'POST'])
@login_required
def book_by_disease():
    db = get_db()
    if request.method == 'POST':
        disease = request.form['disease']
        date = request.form['appointment_date']
        slot = request.form['time_slot']
        symptoms = request.form.get('symptoms', '')

        spec_name = DISEASE_SPEC_MAP.get(disease)
        if not spec_name:
            flash('Could not find a specialization for this disease.', 'danger')
            return redirect(url_for('book_by_disease'))

        spec = db.execute("SELECT id FROM specializations WHERE name=?", (spec_name,)).fetchone()
        if not spec:
            flash('Specialization not found.', 'danger')
            return redirect(url_for('book_by_disease'))

        # Find an available doctor in that specialization
        doctor = db.execute("""
            SELECT d.id, d.full_name FROM doctors d
            WHERE d.specialization_id=? AND d.is_available=1
            AND d.id NOT IN (
                SELECT doctor_id FROM appointments
                WHERE appointment_date=? AND time_slot=? AND status != 'Cancelled'
            )
            LIMIT 1
        """, (spec['id'], date, slot)).fetchone()

        if not doctor:
            flash('No available doctor for this disease at the selected time. Try a different slot.', 'warning')
            return redirect(url_for('book_by_disease'))

        receipt_no = 'HMS' + datetime.now().strftime('%Y%m%d%H%M%S')
        db.execute("""INSERT INTO appointments (receipt_no, user_id, doctor_id, appointment_date,
                      time_slot, booking_type, disease, symptoms, status)
                      VALUES (?, ?, ?, ?, ?, 'Disease', ?, ?, 'Scheduled')""",
                   (receipt_no, session['user_id'], doctor['id'], date, slot, disease, symptoms))
        db.commit()
        apt = db.execute("SELECT id FROM appointments WHERE receipt_no=?", (receipt_no,)).fetchone()
        flash('Appointment booked! Assigned to Dr. ' + doctor['full_name'], 'success')
        return redirect(url_for('receipt', apt_id=apt['id']))

    return render_template('book_by_disease.html', diseases=list(DISEASE_SPEC_MAP.keys()),
                           time_slots=TIME_SLOTS)

@app.route('/get-slots')
@login_required
def get_slots():
    doctor_id = request.args.get('doctor_id')
    date = request.args.get('date')
    if not doctor_id or not date:
        return jsonify([])
    db = get_db()
    booked = db.execute("""SELECT time_slot FROM appointments
        WHERE doctor_id=? AND appointment_date=? AND status != 'Cancelled'""",
        (doctor_id, date)).fetchall()
    booked_slots = [r['time_slot'] for r in booked]
    result = []
    for slot in TIME_SLOTS:
        result.append({'slot': slot, 'booked': slot in booked_slots})
    return jsonify(result)

@app.route('/my-appointments')
@login_required
def my_appointments():
    db = get_db()
    appointments = db.execute("""
        SELECT a.*, d.full_name as doctor_name, s.name as specialization
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        JOIN specializations s ON d.specialization_id = s.id
        WHERE a.user_id=?
        ORDER BY a.created_at DESC
    """, (session['user_id'],)).fetchall()
    return render_template('my_appointments.html', appointments=appointments)

@app.route('/cancel-appointment/<int:apt_id>', methods=['POST'])
@login_required
def cancel_appointment(apt_id):
    db = get_db()
    db.execute("UPDATE appointments SET status='Cancelled' WHERE id=? AND user_id=?",
               (apt_id, session['user_id']))
    db.commit()
    flash('Appointment cancelled.', 'info')
    return redirect(url_for('my_appointments'))

@app.route('/receipt/<int:apt_id>')
@login_required
def receipt(apt_id):
    db = get_db()
    apt = db.execute("""
        SELECT a.*, d.full_name as doctor_name, d.qualification, d.experience,
               s.name as specialization, u.full_name as patient_name,
               u.email as patient_email, u.phone as patient_phone,
               u.gender as patient_gender, u.blood_group as patient_blood,
               u.dob as patient_dob
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        JOIN specializations s ON d.specialization_id = s.id
        JOIN users u ON a.user_id = u.id
        WHERE a.id=? AND a.user_id=?
    """, (apt_id, session['user_id'])).fetchone()
    if not apt:
        flash('Appointment not found.', 'danger')
        return redirect(url_for('my_appointments'))
    return render_template('receipt.html', apt=apt)

#  ADMIN ROUTES

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()

        # Check admin
        admin = db.execute("SELECT * FROM admins WHERE username=?", (username,)).fetchone()
        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['username']
            flash('Welcome, Admin!', 'success')
            return redirect(url_for('admin_dashboard'))

        # Check doctor
        doctor = db.execute("""SELECT d.*, s.name as specialization FROM doctors d
                              JOIN specializations s ON d.specialization_id = s.id
                              WHERE d.username=?""", (username,)).fetchone()
        if doctor and check_password_hash(doctor['password_hash'], password):
            session['doctor_id'] = doctor['id']
            session['doctor_name'] = doctor['full_name']
            flash('Welcome, Dr. ' + doctor['full_name'] + '!', 'success')
            return redirect(url_for('doctor_dashboard'))

        flash('Invalid credentials.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    session.pop('doctor_id', None)
    session.pop('doctor_name', None)
    flash('Logged out.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    db = get_db()
    total_doctors = db.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
    total_patients = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    total_appointments = db.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    scheduled = db.execute("SELECT COUNT(*) FROM appointments WHERE status='Scheduled'").fetchone()[0]
    recent = db.execute("""
        SELECT a.*, u.full_name as patient_name, d.full_name as doctor_name,
               s.name as specialization
        FROM appointments a
        JOIN users u ON a.user_id = u.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN specializations s ON d.specialization_id = s.id
        ORDER BY a.created_at DESC LIMIT 5
    """).fetchall()
    return render_template('admin_dashboard.html', total_doctors=total_doctors,
                           total_patients=total_patients, total_appointments=total_appointments,
                           scheduled=scheduled, recent=recent)

@app.route('/admin/doctors')
@admin_required
def admin_doctors():
    db = get_db()
    doctors = db.execute("""
        SELECT d.*, s.name as specialization
        FROM doctors d JOIN specializations s ON d.specialization_id = s.id
        ORDER BY d.full_name
    """).fetchall()
    specs = db.execute("SELECT * FROM specializations ORDER BY name").fetchall()
    return render_template('admin_doctors.html', doctors=doctors, specializations=specs)

@app.route('/admin/doctors/add', methods=['POST'])
@admin_required
def add_doctor():
    db = get_db()
    
    username = request.form['username']
    email = request.form['email']
    phone = request.form['phone']
    
    # Check for duplicates among doctors
    existing = db.execute("SELECT id FROM doctors WHERE username=? OR email=? OR phone=?", 
                          (username, email, phone)).fetchone()
    if existing:
        flash('A doctor with that username, email, or phone number already exists.', 'danger')
        return redirect(url_for('admin_doctors'))

    db.execute("""INSERT INTO doctors (full_name, username, password_hash, email, phone,
                  specialization_id, qualification, experience, bio)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
               (request.form['full_name'], username,
                generate_password_hash(request.form['password']),
                email, phone,
                request.form['specialization_id'], request.form['qualification'],
                request.form['experience'], request.form.get('bio', '')))
    db.commit()
    flash('Doctor added successfully!', 'success')
    return redirect(url_for('admin_doctors'))

@app.route('/admin/doctors/edit/<int:doc_id>', methods=['POST'])
@admin_required
def edit_doctor(doc_id):
    db = get_db()
    
    username = request.form['username']
    email = request.form['email']
    phone = request.form['phone']
    
    # Check if another doctor is using these details
    existing = db.execute("SELECT id FROM doctors WHERE (username=? OR email=? OR phone=?) AND id!=?", 
                          (username, email, phone, doc_id)).fetchone()
    if existing:
        flash('Another doctor is already using that username, email, or phone number.', 'danger')
        return redirect(url_for('admin_doctors'))

    password = request.form.get('password', '')
    if password:
        db.execute("""UPDATE doctors SET full_name=?, username=?, email=?, phone=?,
                      specialization_id=?, qualification=?, experience=?, bio=?,
                      password_hash=? WHERE id=?""",
                   (request.form['full_name'], username, email, phone,
                    request.form['specialization_id'], request.form['qualification'],
                    request.form['experience'], request.form.get('bio', ''),
                    generate_password_hash(password), doc_id))
    else:
        db.execute("""UPDATE doctors SET full_name=?, username=?, email=?, phone=?,
                      specialization_id=?, qualification=?, experience=?, bio=?
                      WHERE id=?""",
                   (request.form['full_name'], username, email, phone,
                    request.form['specialization_id'], request.form['qualification'],
                    request.form['experience'], request.form.get('bio', ''), doc_id))
    db.commit()
    flash('Doctor updated.', 'success')
    return redirect(url_for('admin_doctors'))

@app.route('/admin/doctors/delete/<int:doc_id>', methods=['POST'])
@admin_required
def delete_doctor(doc_id):
    db = get_db()
    db.execute("DELETE FROM appointments WHERE doctor_id=?", (doc_id,))
    db.execute("DELETE FROM doctors WHERE id=?", (doc_id,))
    db.commit()
    flash('Doctor deleted.', 'info')
    return redirect(url_for('admin_doctors'))

@app.route('/admin/doctors/toggle/<int:doc_id>', methods=['POST'])
@admin_required
def toggle_doctor(doc_id):
    db = get_db()
    doc = db.execute("SELECT is_available FROM doctors WHERE id=?", (doc_id,)).fetchone()
    new_val = 0 if doc['is_available'] else 1
    db.execute("UPDATE doctors SET is_available=? WHERE id=?", (new_val, doc_id))
    db.commit()
    flash('Doctor availability updated.', 'success')
    return redirect(url_for('admin_doctors'))

@app.route('/admin/services')
@admin_required
def admin_services():
    db = get_db()
    all_services = db.execute("SELECT * FROM services ORDER BY name").fetchall()
    return render_template('admin_services.html', services=all_services)

@app.route('/admin/services/add', methods=['POST'])
@admin_required
def add_service():
    db = get_db()
    db.execute("INSERT INTO services (name, description, icon) VALUES (?, ?, ?)",
               (request.form['name'], request.form['description'], request.form.get('icon', 'bi-heart-pulse')))
    db.commit()
    flash('Service added!', 'success')
    return redirect(url_for('admin_services'))

@app.route('/admin/services/edit/<int:svc_id>', methods=['POST'])
@admin_required
def edit_service(svc_id):
    db = get_db()
    is_active = 1 if request.form.get('is_active') else 0
    db.execute("UPDATE services SET name=?, description=?, icon=?, is_active=? WHERE id=?",
               (request.form['name'], request.form['description'],
                request.form.get('icon', 'bi-heart-pulse'), is_active, svc_id))
    db.commit()
    flash('Service updated.', 'success')
    return redirect(url_for('admin_services'))

@app.route('/admin/services/delete/<int:svc_id>', methods=['POST'])
@admin_required
def delete_service(svc_id):
    db = get_db()
    db.execute("DELETE FROM services WHERE id=?", (svc_id,))
    db.commit()
    flash('Service deleted.', 'info')
    return redirect(url_for('admin_services'))

@app.route('/admin/appointments')
@admin_required
def admin_appointments():
    db = get_db()
    status_filter = request.args.get('status', 'All')
    if status_filter and status_filter != 'All':
        appointments = db.execute("""
            SELECT a.*, u.full_name as patient_name, d.full_name as doctor_name,
                   s.name as specialization
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN specializations s ON d.specialization_id = s.id
            WHERE a.status=?
            ORDER BY a.created_at DESC
        """, (status_filter,)).fetchall()
    else:
        appointments = db.execute("""
            SELECT a.*, u.full_name as patient_name, d.full_name as doctor_name,
                   s.name as specialization
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN specializations s ON d.specialization_id = s.id
            ORDER BY a.created_at DESC
        """).fetchall()
    return render_template('admin_appointments.html', appointments=appointments,
                           current_filter=status_filter)

@app.route('/admin/appointments/update/<int:apt_id>', methods=['POST'])
@admin_required
def admin_update_appointment(apt_id):
    db = get_db()
    db.execute("UPDATE appointments SET status=? WHERE id=?",
               (request.form['status'], apt_id))
    db.commit()
    flash('Appointment status updated.', 'success')
    return redirect(url_for('admin_appointments'))

@app.route('/admin/patients')
@admin_required
def admin_patients():
    db = get_db()
    patients = db.execute("""
        SELECT u.*, (SELECT COUNT(*) FROM appointments WHERE user_id=u.id) as apt_count
        FROM users u ORDER BY u.created_at DESC
    """).fetchall()
    return render_template('admin_patients.html', patients=patients)

#  DOCTOR ROUTES

@app.route('/doctor/dashboard')
@doctor_required
def doctor_dashboard():
    db = get_db()
    did = session['doctor_id']
    doctor = db.execute("SELECT * FROM doctors WHERE id=?", (did,)).fetchone()
    total = db.execute("SELECT COUNT(*) FROM appointments WHERE doctor_id=?", (did,)).fetchone()[0]
    scheduled = db.execute("SELECT COUNT(*) FROM appointments WHERE doctor_id=? AND status='Scheduled'", (did,)).fetchone()[0]
    completed = db.execute("SELECT COUNT(*) FROM appointments WHERE doctor_id=? AND status='Completed'", (did,)).fetchone()[0]
    upcoming = db.execute("""
        SELECT a.*, u.full_name as patient_name, u.email as patient_email,
               u.phone as patient_phone
        FROM appointments a JOIN users u ON a.user_id = u.id
        WHERE a.doctor_id=? AND a.status='Scheduled'
        ORDER BY a.appointment_date, a.time_slot
    """, (did,)).fetchall()
    return render_template('doctor_dashboard.html', doctor=doctor, total=total,
                           scheduled=scheduled, completed=completed, upcoming=upcoming)

@app.route('/doctor/appointments')
@doctor_required
def doctor_appointments():
    db = get_db()
    did = session['doctor_id']
    status_filter = request.args.get('status', 'All')
    if status_filter and status_filter != 'All':
        appointments = db.execute("""
            SELECT a.*, u.full_name as patient_name, u.email as patient_email,
                   u.phone as patient_phone, u.gender as patient_gender,
                   u.blood_group as patient_blood
            FROM appointments a JOIN users u ON a.user_id = u.id
            WHERE a.doctor_id=? AND a.status=?
            ORDER BY a.appointment_date DESC
        """, (did, status_filter)).fetchall()
    else:
        appointments = db.execute("""
            SELECT a.*, u.full_name as patient_name, u.email as patient_email,
                   u.phone as patient_phone, u.gender as patient_gender,
                   u.blood_group as patient_blood
            FROM appointments a JOIN users u ON a.user_id = u.id
            WHERE a.doctor_id=?
            ORDER BY a.appointment_date DESC
        """, (did,)).fetchall()
    return render_template('doctor_appointments.html', appointments=appointments,
                           current_filter=status_filter)

@app.route('/doctor/prescribe/<int:apt_id>', methods=['POST'])
@doctor_required
def prescribe(apt_id):
    db = get_db()
    prescription = request.form['prescription']
    status = request.form.get('status', 'Completed')
    db.execute("UPDATE appointments SET prescription=?, status=? WHERE id=? AND doctor_id=?",
               (prescription, status, apt_id, session['doctor_id']))
    db.commit()
    flash('Prescription saved and status updated.', 'success')
    return redirect(url_for('doctor_appointments'))

@app.route('/doctor/toggle-availability', methods=['POST'])
@doctor_required
def toggle_own_availability():
    db = get_db()
    did = session['doctor_id']
    doc = db.execute("SELECT is_available FROM doctors WHERE id=?", (did,)).fetchone()
    new_val = 0 if doc['is_available'] else 1
    db.execute("UPDATE doctors SET is_available=? WHERE id=?", (new_val, did))
    db.commit()
    status = 'Available' if new_val else 'Offline'
    flash('You are now ' + status + '.', 'success')
    return redirect(url_for('doctor_dashboard'))

#  Run 

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
