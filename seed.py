"""
seed.py - Database Seeder for HealthCare HMS
Run this script to populate the database with initial data.
Usage: python seed.py
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hospital.db')

def seed_database():
    # Check if database exists
    if not os.path.exists(DATABASE):
        print("[ERROR] hospital.db not found!")
        print("Please run 'python app.py' first to create the database, then run this script.")
        return

    db = sqlite3.connect(DATABASE)
    db.execute("PRAGMA foreign_keys = ON")
    cur = db.cursor()

    print("=" * 50)
    print("  HealthCare HMS - Database Seeder")
    print("=" * 50)

    # ─── 1. Seed Admin ───
    print("\n[1/3] Seeding admin account...")
    existing = cur.execute("SELECT id FROM admins WHERE username='admin'").fetchone()
    if not existing:
        cur.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)",
                     ('admin', generate_password_hash('admin123')))
        print("  ✓ Admin created (username: admin, password: admin123)")
    else:
        print("  - Admin already exists, skipping.")

    # ─── 2. Seed Specializations ───
    print("\n[2/3] Seeding specializations...")
    specializations = [
        'General Medicine',
        'Cardiology',
        'Neurology',
        'Dermatology',
        'Orthopedics',
        'Pediatrics',
        'Gynecology',
        'Ophthalmology',
        'ENT',
        'Endocrinology',
        'Psychiatry'
    ]
    added = 0
    for spec in specializations:
        existing = cur.execute("SELECT id FROM specializations WHERE name=?", (spec,)).fetchone()
        if not existing:
            cur.execute("INSERT INTO specializations (name) VALUES (?)", (spec,))
            added += 1
    print(f"  ✓ {added} specializations added ({len(specializations) - added} already existed)")

    # ─── 3. Seed Services ───
    print("\n[3/3] Seeding services...")
    services = [
        ('Emergency Care', 'Round-the-clock emergency medical services', 'bi-plus-circle'),
        ('Cardiology', 'Heart and cardiovascular care', 'bi-heart-pulse'),
        ('Neurology', 'Brain and nervous system treatment', 'bi-activity'),
        ('Orthopedics', 'Bone and joint care', 'bi-bandaid'),
        ('Pediatrics', 'Healthcare for children', 'bi-emoji-smile'),
        ('Diagnostics & Lab', 'Medical testing and diagnostics', 'bi-clipboard2-pulse'),
        ('Radiology', 'Imaging and scanning services', 'bi-radioactive'),
        ('Surgery', 'Surgical procedures and operations', 'bi-scissors'),
        ('Pharmacy', 'Medicines and prescriptions', 'bi-capsule'),
        ('Physiotherapy', 'Physical rehabilitation', 'bi-person-walking'),
        ('Dermatology', 'Skin care and treatment', 'bi-droplet'),
        ('Mental Health', 'Counseling and psychiatric care', 'bi-chat-heart'),
    ]
    added = 0
    for name, desc, icon in services:
        existing = cur.execute("SELECT id FROM services WHERE name=?", (name,)).fetchone()
        if not existing:
            cur.execute("INSERT INTO services (name, description, icon) VALUES (?, ?, ?)",
                         (name, desc, icon))
            added += 1
    print(f"  ✓ {added} services added ({len(services) - added} already existed)")

    db.commit()
    db.close()

    print("\n" + "=" * 50)
    print("  Seeding complete!")
    print("  Admin login: username='admin', password='admin123'")
    print("=" * 50)


if __name__ == '__main__':
    seed_database()
