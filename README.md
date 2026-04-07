<p align="center">
  <img src="https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django" />
  <img src="https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react" />
  <img src="https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Stripe-Payments-635BFF?style=for-the-badge&logo=stripe&logoColor=white" />
  <img src="https://img.shields.io/badge/Vite-5.3-646CFF?style=for-the-badge&logo=vite&logoColor=white" />
</p>

# SellIt

A production-ready, full-stack peer-to-peer marketplace with escrow payments, two-factor authentication, content moderation, and a complete admin panel. Built with Django REST Framework and React.

> **Live Demo:** [sell-it-kohl.vercel.app](https://sell-it-kohl.vercel.app)

---

## Features

### Core Marketplace
- Fixed-price listings and timed auctions with live countdown
- Multi-image uploads via Cloudinary CDN
- Price negotiation through offer/counter-offer system
- Advanced search with filters (category, condition, price range, listing type)
- Saved search alerts with automatic notifications on new matches
- Favorites / wishlist functionality
- Social sharing (Twitter, Facebook, copy link)

### Payments & Protection
- Stripe payment processing (PaymentIntent API)
- Escrow system — funds held until buyer confirms delivery
- 7-day buyer protection window for disputes
- Automated escrow release after protection period
- PDF shipping label generation (4×6 format)
- Digital receipts

### Safety & Security
- Email verification with UUID tokens
- Two-factor authentication (TOTP — Google Authenticator / Authy)
- Rate limiting (login: 5/min, listing creation: 10/hr)
- Content moderation — banned keyword detection + suspicious pricing flags
- Report system with auto-escalation (3+ reports auto-hides listing)
- User blocking with transaction enforcement
- Buyer reputation scoring based on dispute history
- Activity logging (login, registration, profile changes with IP tracking)

### Communication
- Real-time direct messaging with conversation threads
- 14 notification types (in-app + email via Brevo)
- Unread message and notification badges

### Seller Tools
- Analytics dashboard with revenue tracking
- Search trend charts (top keywords, weekly volume)
- Listing management (draft, active, sold, closed)
- Offer management (accept/reject incoming offers)
- Order fulfillment with tracking numbers

### Admin Panel
- Dashboard with platform-wide statistics
- Dispute resolution (refund / no-refund / close)
- User management (verify, ban, delete)
- Listing oversight and removal
- Report review and dismissal
- Activity logs with IP addresses

---

## Tech Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, React Router 6, Axios, Stripe.js, Recharts |
| **Backend** | Django 5.0, Django REST Framework, SimpleJWT |
| **Database** | PostgreSQL |
| **Payments** | Stripe (PaymentIntent API + Webhooks) |
| **Storage** | Cloudinary (images), WhiteNoise (static files) |
| **Auth** | JWT (access + refresh), TOTP 2FA (PyOTP + QR Code) |
| **Email** | Brevo HTTP API (production), SMTP (development) |
| **PDF** | ReportLab (shipping labels) |
| **Hosting** | Render (backend), Vercel (frontend) |

---

## Project Structure

```
SellIT/
├── backend/
│   ├── users/            # Auth, profiles, 2FA, blocking, activity logs
│   ├── listings/         # Listings, images, offers, bids, search, moderation
│   ├── orders/           # Orders, payments, escrow, reviews, disputes
│   ├── messaging/        # Direct messages between users
│   ├── notifications/    # In-app alerts + email delivery
│   ├── analytics/        # Seller revenue & search trends
│   ├── sellit/           # Django settings & URL config
│   ├── requirements.txt  # Python dependencies
│   ├── build.sh          # Render build script
│   └── Procfile          # Gunicorn process config
│
├── frontend/
│   ├── src/
│   │   ├── pages/        # 23 page components
│   │   ├── components/   # 6 reusable components
│   │   ├── context/      # AuthContext (global state)
│   │   ├── api/          # Axios client + API modules
│   │   ├── App.jsx       # Router & protected routes
│   │   └── styles.css    # Design system
│   ├── vercel.json       # SPA rewrite rules
│   └── package.json      # Node dependencies
│
└── PROJECT_STUDY.md      # Complete technical documentation
```

---

## Prerequisites

| Tool | Version | Download |
|---|---|---|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) |
| PostgreSQL | 15+ | [postgresql.org](https://www.postgresql.org/download/) |
| Git | Any | [git-scm.com](https://git-scm.com/downloads/) |

---

## Local Development Setup

### 1. Clone & Create Database

```bash
git clone https://github.com/jilspatel1412/SellIT.git
cd SellIT

# Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE sellit;"
```

### 2. Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

Create `backend/.env`:

```env
SECRET_KEY=your-random-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/sellit
ALLOWED_HOSTS=localhost,127.0.0.1

# Stripe (https://dashboard.stripe.com/test/apikeys)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Cloudinary (https://cloudinary.com — free tier)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Email (Gmail App Password or Brevo)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your@gmail.com

FRONTEND_URL=http://localhost:5173
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

Run migrations and start:

```bash
python manage.py migrate
python manage.py runserver
```

Backend runs at **http://localhost:8000**

### 3. Frontend

Open a second terminal:

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

Start the dev server:

```bash
npm run dev
```

Frontend runs at **http://localhost:5173**

### 4. Stripe Webhooks (Local)

Payments require Stripe CLI to forward webhooks locally:

```bash
# Install: brew install stripe/stripe-cli/stripe (Mac)
# or download from https://github.com/stripe/stripe-cli/releases

stripe login
stripe listen --forward-to localhost:8000/api/payments/webhook/
```

Copy the `whsec_...` secret it outputs into your `backend/.env` as `STRIPE_WEBHOOK_SECRET`.

---

## Production Deployment

### Backend → Render

1. Create a **Web Service** on [render.com](https://render.com)
2. Connect your GitHub repository
3. Configure:
   - **Root Directory:** `backend`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn sellit.wsgi --log-file -`
4. Add a **PostgreSQL** database (free tier)
5. Set environment variables (see [Environment Variables](#environment-variables))

### Frontend → Vercel

1. Import project on [vercel.com](https://vercel.com)
2. Configure:
   - **Framework:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Output Directory:** `dist`
3. Set environment variables:
   - `VITE_API_BASE_URL` = your Render backend URL
   - `VITE_STRIPE_PUBLISHABLE_KEY` = your Stripe publishable key

### Stripe Webhook (Production)

1. Go to [Stripe Dashboard → Webhooks](https://dashboard.stripe.com/test/webhooks)
2. Add endpoint: `https://<your-backend>/api/payments/webhook/`
3. Select events: `payment_intent.succeeded`, `payment_intent.payment_failed`
4. Copy signing secret → set as `STRIPE_WEBHOOK_SECRET` on Render

---

## Environment Variables

### Backend

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key (random string) |
| `DEBUG` | `True` for development, `False` for production |
| `DATABASE_URL` | PostgreSQL connection string |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `FRONTEND_URL` | Frontend origin URL |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins |
| `STRIPE_SECRET_KEY` | Stripe secret key (`sk_test_...`) |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret (`whsec_...`) |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |
| `BREVO_API_KEY` | Brevo API key (production email) |
| `DEFAULT_FROM_EMAIL` | Sender email address |
| `ADMIN_USERNAME` | Auto-created admin username |
| `ADMIN_EMAIL` | Auto-created admin email |
| `ADMIN_PASSWORD` | Auto-created admin password |

### Frontend

| Variable | Description |
|---|---|
| `VITE_API_BASE_URL` | Backend API URL |
| `VITE_STRIPE_PUBLISHABLE_KEY` | Stripe publishable key (`pk_test_...`) |

---

## Test Cards (Stripe)

| Card Number | Result |
|---|---|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 0002` | Card declined |

Use any future expiry date and any 3-digit CVC.

---

## Management Commands

| Command | Purpose |
|---|---|
| `python manage.py migrate` | Apply database migrations |
| `python manage.py create_admin` | Create admin user from env vars |
| `python manage.py seed_categories` | Seed 12 default product categories |
| `python manage.py settle_auctions` | Close expired auctions and notify winners |
| `python manage.py release_escrow` | Auto-release escrow after protection period |

`seed_categories` runs automatically via data migration. `settle_auctions` and `release_escrow` should be set up as scheduled tasks (cron) in production.

---

## API Overview

| Module | Base Path | Endpoints |
|---|---|---|
| Auth & Users | `/api/auth/` | Register, login, 2FA, profiles, blocking |
| Listings | `/api/listings/` | CRUD, search, offers, bids, favorites, reports |
| Orders | `/api/orders/` | Orders, status updates, reviews, disputes |
| Payments | `/api/payments/` | Stripe intents, webhooks |
| Messages | `/api/messages/` | Threads, send/receive |
| Notifications | `/api/notifications/` | List, mark read |
| Analytics | `/api/analytics/` | Revenue, search trends |

Full API reference with all endpoints, methods, and parameters is available in [PROJECT_STUDY.md](PROJECT_STUDY.md).

---

## Team

| Member | Responsibility |
|---|---|
| **Jils** | Authentication, security, 2FA, deployment |
| **Hetu** | Listings, search, auctions, moderation |
| **Utsav** | Orders, payments, escrow, reviews |
| **Hitarth** | Messaging, notifications, disputes, admin panel |

---

## License

This project was built for educational purposes.
