# HealthCare Hospital Management System (HMS)

> **Live Demo:** [https://hospital-management-system-080i.onrender.com/](https://hospital-management-system-080i.onrender.com/)

HealthCare HMS is a comprehensive, full-stack Hospital Management System built with Python, Flask, and SQLite. It provides a robust scheduling and management platform designed to streamline interactions between Administrators, Doctors, and Patients.

## 🌟 Key Features

### 👤 Patient Portal
- **Smart Booking System:** Patients can easily book appointments by selecting a specific doctor, or by choosing their **Symptoms/Disease** (the system intelligently maps their illness to the correct medical specialist).
- **Appointment History & Receipts:** Patients can view all their upcoming, completed, and cancelled appointments. After booking, an official generated receipt is provided for tracking.
- **Secure Authentication:** Complete account creation and login system employing strong password hashing.

### 🩺 Doctor Dashboard
- **Schedule Management:** Doctors receive a specialized dashboard to view and manage their assigned daily appointments in real-time.
- **Prescription System:** Allows primary care providers to directly attach prescriptions and diagnosis notes to a patient's appointment and resolve them.
- **Availability Toggle:** Doctors can independently switch their status between "Available" and "Offline", removing them from the patient booking pool when off-shift.

### 🛡️ Admin Panel
- **Comprehensive Oversight:** System administrators have a high-level overview of total operations (Total Patients, Total Doctors, and Appointment Statistics).
- **Manage Personnel:** Full CRUD functionality to add new doctors to the system, update qualifications, remove accounts, or manually override doctor availability.
- **Service Management:** Maintain the dynamically rendered list of hospital services and medical specializations.
- **Appointment Filters:** View and filter all hospital-wide appointments chronologically or by status.

## 🚀 Tech Stack
- **Backend:** Python 3, Flask, Werkzeug (Password Security)
- **Database:** SQLite3
- **Frontend / UI:** HTML5, CSS3, pre-built templates rendered with Jinja2
- **Production Server:** Gunicorn

## 🛠️ Local Installation

If you'd like to run this application locally on your machine, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lalith-kumar-raju/Hospital-Management-System.git
   cd Hospital-Management-System
   ```

2. **Install dependencies:**
   Make sure you have Python installed, then install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the Database:**
   You can quickly populate your database with dummy admin, doctor, and user accounts by running the included seed script:
   ```bash
   python seed.py
   ```
   *(See `credentials.txt` for the generated login credentials if needed)*

4. **Run the Application:**
   ```bash
   python app.py
   ```
   *The system will be accessible locally at `http://127.0.0.1:5000`.*
