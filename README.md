# 🏔️ TrekMate — Trekking Management Application

TrekMate is a role-based web application for managing trekking expeditions — built with Flask, SQLAlchemy, and Bootstrap.
It supports three distinct roles (**Admin**, **Trek Staff**, and **Trekker/User**), each with their own dashboard and permissions, covering 
the full lifecycle of a trek from creation to booking to completion.

---

## ✨ Features

### 👑 Admin
- Dashboard with live stats (total treks, users, staff, bookings, open/pending/completed treks)
- Full CRUD on treks (create, edit, delete, update status)
- Add staff directly, or approve/reject staff self-registrations
- Assign staff to treks
- Search & manage users and staff (blacklist/activate)
- View and filter all bookings across the platform, with payment status
- Assign staff to treks

### 🧭 Trek Staff
- Self-register (account requires admin approval before login)
- Dashboard showing only treks assigned to them
- Update available slots and trek status (Open / Closed / Completed)
- View and manage the participant list for each assigned trek
- Update payment status (Pending / Paid / Refunded) per participant
- Edit own profile (name, email, password)

### 🥾 Trekker (User)
- Register and log in
- Browse open treks, filterable by **difficulty** and **location**
- Book a trek (with duplicate-booking and overbooking prevention)
- Cancel an existing booking
- View full trekking history with booking and payment status
- Mark a booking as paid (self-service "Pay Now")
- Edit own profile

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask |
| ORM / Database | Flask-SQLAlchemy + SQLite |
| Templating | Jinja2 |
| Styling | Bootstrap 5 + custom CSS |
| Config | python-dotenv |

---

## 📁 Project Structure

```
TrekMate/
├── app.py                 # Flask app entry point
├── config.py               # Loads environment config (.env)
├── models.py                # SQLAlchemy models (User, Trek, Booking) + admin seed
├── routes.py                 # All route/controller logic, grouped by role
├── requirements.txt
├── static/
│   ├── style.css              # Custom theme
│   └── images/
└── templates/
    ├── base.html               # Shared layout, navbar block, flash messages
    ├── index.html, login.html, register.html, register_staff.html
    ├── admin/                   # Admin dashboard, trek/staff/user management, bookings
    ├── staff/                    # Staff dashboard, trek management, profile
    └── user/                      # User dashboard, trek browsing, profile, bookings
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd TrekMate
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
SQLALCHEMY_DATABASE_URI=sqlite:///instance/db.sqlite3
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

### 5. Run the app
```bash
flask run
```
The database (`db.sqlite3`) and tables are created automatically on first run, along with a default admin account.

Visit **http://127.0.0.1:5000** in your browser.

---

## 🔑 Default Admin Login

| Username | Password |
|---|---|
| `admin` | `admin` |

> ⚠️ Change this password after first login in a real deployment — it's seeded in plaintext for local development only.

---

## 🧑‍🤝‍🧑 Trying Out Each Role

1. **As Admin** — log in with the default credentials above, add a trek, add or approve staff, and assign staff to a trek.
2. **As Staff** — register via the "Register as Staff" link, then have the admin approve the account under **Pending Staff** before logging in.
3. **As User** — register normally, browse open treks, and book one.

---

## 🗄️ Database Schema (Summary)

- **User** — `id, username, name, password, email, role (admin/staff/user), is_blacklisted, is_approved, created_date`
- **Trek** — `id, name, location, difficulty, duration, total_slots, available_slots, assigned_staff_id (FK→User), status, start_date, end_date, price, description`
- **Booking** — `id, user_id (FK→User), trek_id (FK→Trek), booking_date, status (Booked/Cancelled/Completed), payment_status (Pending/Paid/Refunded)`

Trek status flow: `Pending → Approved → Open → Closed/Completed` (new treks require admin sign-off before staff can open them for booking).

---

## 📌 Notes

- All state-changing actions (booking, cancellation, status/payment updates) are POST-only routes.
- Session-based authentication with role checks on every protected route.
- Available slots are recalculated server-side from live booking counts to avoid drift.

---

## 📄 License

This project was built as part of an academic coursework submission.
