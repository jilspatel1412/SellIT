# SellIt Marketplace — Standard Operating Procedure (SOP)

| | |
|---|---|
| **Document ID** | SOP-SELLIT-001 |
| **Version** | 2.0 |
| **Effective Date** | April 7, 2026 |
| **Classification** | Internal — Engineering |
| **Prepared By** | Jils Patel, Hetu Patel, Utsav Patel, Hitarth Patel |
| **Status** | Final |

---

## Table of Contents

1. [Purpose & Scope](#1-purpose--scope)
2. [System Overview](#2-system-overview)
3. [Roles & Responsibilities](#3-roles--responsibilities)
4. [System Architecture](#4-system-architecture)
5. [Technology Stack](#5-technology-stack)
6. [Database Design](#6-database-design)
7. [API Reference](#7-api-reference)
8. [Frontend Application](#8-frontend-application)
9. [Standard Operating Procedures](#9-standard-operating-procedures)
   - 9.1 [User Registration & Authentication](#91-user-registration--authentication)
   - 9.2 [Listing Management](#92-listing-management)
   - 9.3 [Purchase & Payment Processing](#93-purchase--payment-processing)
   - 9.4 [Escrow & Buyer Protection](#94-escrow--buyer-protection)
   - 9.5 [Dispute Resolution](#95-dispute-resolution)
   - 9.6 [Content Moderation](#96-content-moderation)
   - 9.7 [Two-Factor Authentication](#97-two-factor-authentication)
10. [Security Policies](#10-security-policies)
11. [Deployment Procedures](#11-deployment-procedures)
12. [Environment Configuration](#12-environment-configuration)
13. [Scheduled Maintenance Tasks](#13-scheduled-maintenance-tasks)
14. [Software Development Lifecycle](#14-software-development-lifecycle)

---

## 1. Purpose & Scope

### 1.1 Purpose

This Standard Operating Procedure defines the architecture, technical specifications, operational workflows, security policies, and deployment procedures for the **SellIt Marketplace** platform. It serves as the single source of truth for all engineering, operational, and academic review purposes.

### 1.2 Scope

This document covers:
- System architecture and technology decisions
- Database design across 6 Django applications and 20 models
- All 54 REST API endpoints
- All 23 frontend pages and 6 shared components
- End-to-end operational procedures (registration, listing, purchase, payment, escrow, disputes)
- Security policies (authentication, authorization, rate limiting, content moderation)
- Deployment and environment configuration
- Software development lifecycle methodology

### 1.3 Definitions

| Term | Definition |
|---|---|
| **SPA** | Single Page Application — browser loads once, React handles navigation |
| **JWT** | JSON Web Token — signed token for stateless authentication |
| **TOTP** | Time-based One-Time Password — 6-digit code that changes every 30 seconds |
| **Escrow** | Payment holding mechanism — funds released after buyer confirms delivery |
| **PaymentIntent** | Stripe object representing a single payment lifecycle |
| **ORM** | Object-Relational Mapping — database abstraction layer in Django |
| **CDN** | Content Delivery Network — global file distribution (Cloudinary) |
| **CORS** | Cross-Origin Resource Sharing — browser security policy for cross-domain requests |
| **WSGI** | Web Server Gateway Interface — protocol between Gunicorn and Django |
| **PCI DSS** | Payment Card Industry Data Security Standard — card data handling rules |

### 1.4 Live Endpoints

| Environment | URL |
|---|---|
| Frontend (Production) | https://sell-it-kohl.vercel.app |
| Backend API (Production) | https://sellit-ma71.onrender.com |
| Source Repository | https://github.com/jilspatel1412/SellIT |

---

## 2. System Overview

SellIt is a full-stack peer-to-peer marketplace where users register as buyers or sellers to trade items with built-in payment protection. The platform supports:

- **Fixed-price listings** with instant Buy Now and negotiable offers
- **Auction listings** with timed bidding and live countdown
- **Stripe payment processing** with escrow protection
- **7-day buyer protection** after delivery confirmation
- **Two-factor authentication** via TOTP (Google Authenticator / Authy)
- **Content moderation** with automated keyword detection and report escalation
- **Admin moderation panel** for dispute resolution, user management, and activity monitoring
- **Direct messaging** between buyers and sellers
- **Transactional emails** via Brevo HTTP API (11 professional HTML templates)
- **Seller analytics** with revenue tracking and search trend charts

### Key Metrics

| Metric | Count |
|---|---|
| Django Applications | 6 |
| Database Models | 20 |
| REST API Endpoints | 54 |
| Frontend Pages | 23 |
| Reusable Components | 6 |
| HTML Email Templates | 11 |
| Notification Types | 14 |
| Product Categories | 12 |

---

## 3. Roles & Responsibilities

### 3.1 User Roles

| Role | Permissions |
|---|---|
| **Buyer** | Browse, search, purchase, make offers, place bids, message sellers, write reviews, open disputes, manage favorites, set search alerts |
| **Seller** | All buyer permissions + create/edit/delete listings, manage offers, accept bids, ship orders, view analytics dashboard |
| **Admin** | Moderator only — resolve disputes, manage users (verify/ban/delete), review reports, delete listings, view activity logs. Cannot buy, sell, bid, or make offers. |

### 3.2 Team Responsibilities

| Member | Domain | Backend | Frontend |
|---|---|---|---|
| **Jils Patel** | Auth, Security, Deployment | Users app (registration, login, email verification, password reset), 2FA (TOTP setup/verify/disable), activity logging, rate limiting, deployment config (settings.py, build.sh, Procfile, CORS) | Login, Register, VerifyEmail, ResetPassword, Profile (2FA UI), AuthContext, Navbar |
| **Hetu** | Listings, Search, Moderation | Listings app (CRUD, images, categories), search/filter system, offers (make/accept/reject), auctions (bids, settle command), content moderation, report system, search alerts, seed_categories | Home, Listings, ListingDetail (share/report), CreateListing, EditListing, SellerListings, SellerOffers, BuyerFavorites, SearchAlerts, ListingCard, ImageGallery, BidForm, OfferForm, Countdown |
| **Utsav** | Orders, Payments, Reviews | Orders app (order lifecycle), Stripe integration (PaymentIntent, webhooks, confirm), escrow system (hold/release/refund), release_escrow command, reviews with images, shipping label PDF, receipts | BuyerOrders (escrow, review modal, dispute modal), SellerOrders (ship modal), Checkout (Stripe Elements), OrderDetail (progress tracker) |
| **Hitarth** | Messaging, Notifications, Admin | Messaging app (threads, send/receive, unread count), notifications app (in-app + Brevo emails), analytics app (revenue, search trends), disputes (open/resolve, escrow freeze), user blocking, buyer reputation, admin endpoints | Inbox, DisputeCenter, SupportPanel (5-tab admin), SellerDashboard (charts), SellerProfile (block, reviews) |

---

## 4. System Architecture

```
+-----------------------------------------------------------+
|                    FRONTEND (Vercel)                        |
|  React 18 + Vite SPA                                      |
|  +----------+ +----------+ +----------+ +----------+      |
|  |  Pages   | |Components| |  Context  | | API Layer|      |
|  | (23 pgs) | |(6 shared)| |(AuthCtx)  | | (Axios)  |      |
|  +----------+ +----------+ +----------+ +----+-----+      |
+-----------------------------------------------+------------+
                                                | HTTPS / JWT
+-----------------------------------------------+------------+
|                   BACKEND (Render)                          |
|  Django 5.0 + DRF + Gunicorn                               |
|  +--------+ +--------+ +--------+ +--------+              |
|  | Users  | |Listings| | Orders | |  Msgs  |              |
|  |  App   | |  App   | |  App   | |  App   |              |
|  +--------+ +--------+ +--------+ +--------+              |
|  +-------------+ +------------+                             |
|  |Notifications| | Analytics  |                             |
|  |    App      | |    App     |                             |
|  +------+------+ +------------+                             |
+---------+--------------------------------------------------+
          |
    +-----+-----+  +----------+  +----------+  +--------+
    | PostgreSQL |  |Cloudinary|  |  Stripe  |  | Brevo  |
    |    (DB)    |  | (Images) |  |(Payments)|  |(Emails)|
    +------------+  +----------+  +----------+  +--------+
```

### 4.1 Data Flow

1. User interacts with React UI
2. React sends HTTP request via Axios (JWT token in `Authorization` header)
3. Request reaches Django REST Framework on Render (via Gunicorn)
4. Django authenticates JWT, processes business logic, queries PostgreSQL
5. Returns JSON response
6. React updates the UI

For payments: card details go directly from the browser to Stripe (never touch our server). Stripe returns confirmation. Frontend then calls our `/api/payments/confirm/` endpoint to verify server-side.

### 4.2 Backend Application Structure

| App | Models | Responsibility |
|---|---|---|
| `users` | User, ActivityLog, BlockedUser | Authentication, profiles, 2FA, blocking, activity logs, admin user management |
| `listings` | Category, Listing, ListingImage, Offer, Bid, SearchLog, ListingReport, SearchAlert, UserInteraction | Listings CRUD, images, categories, offers, bids, auctions, search, favorites, reports, moderation |
| `orders` | Order, Payment, Review, ReviewImage, Dispute, Receipt | Orders, Stripe payments, escrow, shipping labels, reviews, disputes, receipts |
| `messaging` | Message | Direct messages between users, conversation threads |
| `notifications` | Notification, EmailLog | In-app notifications, email sending via Brevo/SMTP |
| `analytics` | — (uses Listing, Order, SearchLog) | Seller revenue dashboard, search trend tracking |

---

## 5. Technology Stack

### 5.1 Backend

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Backend language |
| Django | 5.0 | Web framework — ORM, migrations, middleware, admin |
| Django REST Framework | 3.16 | REST API — serializers, views, permissions, throttling |
| djangorestframework-simplejwt | — | JWT authentication (access + refresh tokens) |
| django-cors-headers | — | CORS handling for cross-origin frontend requests |
| python-decouple | — | Environment variable management from `.env` files |
| dj-database-url | — | Parse `DATABASE_URL` into Django database config |
| Gunicorn | — | Production WSGI server (multi-worker) |
| WhiteNoise | — | Static file serving with caching and gzip |
| Stripe (Python SDK) | 14.4 | PaymentIntent creation, refunds, webhook verification |
| PyOTP | 2.9 | TOTP secret generation and code verification for 2FA |
| qrcode | 8.2 | QR code generation for 2FA setup |
| ReportLab | 4.2 | PDF generation (shipping labels, 4x6 inch format) |
| Pillow | — | Image processing for Django `ImageField` |
| Cloudinary + django-cloudinary-storage | — | Cloud image storage and CDN |
| requests | — | HTTP client for Brevo email API |
| psycopg2-binary | — | PostgreSQL database adapter |

### 5.2 Frontend

| Technology | Version | Purpose |
|---|---|---|
| React | 18.3 | Component-based UI library (SPA) |
| Vite | 5.3 | Build tool and dev server (fast HMR) |
| React Router | 6.26 | Client-side routing with protected routes |
| Axios | 1.7 | HTTP client with JWT interceptors (auto-refresh) |
| Stripe.js + @stripe/react-stripe-js | 4.0 / 2.7 | Secure payment form (PCI-compliant CardElement) |
| Recharts | 2.12 | Charts for seller analytics (BarChart) |
| CSS (custom) | — | Hand-written design system — dark theme, CSS variables |

### 5.3 Infrastructure

| Service | Purpose |
|---|---|
| Render | Backend hosting (web service) + managed PostgreSQL database |
| Vercel | Frontend hosting with global CDN and SPA routing |
| Cloudinary | Image storage and CDN for listing photos, avatars, review images |
| Stripe | Payment processing gateway (test mode) |
| Brevo (Sendinblue) | Transactional email delivery via HTTP API |
| GitHub | Source code repository with auto-deploy to Render and Vercel |

---

## 6. Database Design

### 6.1 Entity-Relationship Summary

The system contains **20 models** across **6 Django apps**. All tables use Django's auto-incrementing `BigAutoField` as primary key.

### 6.2 Users App (3 models)

**`users` table** — Custom User (extends AbstractUser)

| Field | Type | Notes |
|---|---|---|
| id | BigAutoField | Primary key |
| username | CharField | Unique |
| email | EmailField | Unique |
| password | CharField | PBKDF2 + SHA256 hashed |
| role | CharField | `'buyer'`, `'seller'`, or `'admin'` |
| is_verified | BooleanField | Email verified (default: false) |
| avatar | ImageField | Profile picture (Cloudinary) |
| bio | TextField | User bio |
| phone_number | CharField | Unique, optional |
| address_line1 | CharField | Street address |
| city | CharField | City |
| state_province | CharField | Province / state |
| postal_code | CharField | Postal / zip code |
| country | CharField | Country |
| is_verified_seller | BooleanField | Admin-granted seller badge |
| verification_token | UUIDField | Email verification link token |
| password_reset_token | UUIDField | Password reset link token |
| password_reset_requested_at | DateTimeField | Reset token expiry tracking |
| totp_secret | CharField(64) | TOTP secret for 2FA |
| is_2fa_enabled | BooleanField | Whether 2FA is active |
| date_joined | DateTimeField | Auto-set on creation |

**`activity_logs` table**

| Field | Type | Notes |
|---|---|---|
| user | FK -> User | CASCADE |
| action | CharField | `'login'`, `'login_failed'`, `'register'`, `'password_reset'`, `'profile_update'`, `'2fa_enabled'`, `'2fa_disabled'` |
| ip_address | GenericIPAddress | Client IP (from X-Forwarded-For) |
| user_agent | CharField(500) | Browser user agent |
| created_at | DateTimeField | Auto-set |

**`blocked_users` table**

| Field | Type | Notes |
|---|---|---|
| blocker | FK -> User | Who blocked |
| blocked | FK -> User | Who got blocked |
| created_at | DateTimeField | Auto-set |
| | | `unique_together: (blocker, blocked)` |

### 6.3 Listings App (9 models)

**`listings_category` table**

| Field | Type | Notes |
|---|---|---|
| name | CharField | Unique (e.g., "Electronics") |
| slug | SlugField | Unique, URL-safe |
| icon | CharField | Emoji or icon code |

**`listings_listing` table**

| Field | Type | Notes |
|---|---|---|
| seller | FK -> User | CASCADE |
| category | FK -> Category | SET_NULL, optional |
| title | CharField | Listing title |
| description | TextField | Full description |
| price | Decimal(12,2) | Price in CAD |
| is_negotiable | BooleanField | Accepts offers |
| condition | CharField | `'new'`, `'used'`, `'refurbished'` |
| status | CharField | `'draft'`, `'active'`, `'sold'`, `'closed'` (indexed) |
| auction_end_time | DateTimeField | Null if fixed-price |
| current_bid | Decimal(12,2) | Highest bid (null if no bids) |
| is_flagged | BooleanField | Content moderation flag |
| flagged_reason | CharField(255) | Moderation reason |
| created_at | DateTimeField | Auto-set (indexed) |
| updated_at | DateTimeField | Auto-updated |

**`listings_listingimage` table**

| Field | Type | Notes |
|---|---|---|
| listing | FK -> Listing | CASCADE |
| image | ImageField | Cloudinary upload |
| url | URLField | Direct URL |
| order | PositiveInteger | Display order |

**`listings_offer` table**

| Field | Type | Notes |
|---|---|---|
| listing | FK -> Listing | CASCADE |
| buyer | FK -> User | CASCADE |
| offer_price | Decimal(12,2) | Offered price |
| status | CharField | `'PENDING'`, `'ACCEPTED'`, `'REJECTED'`, `'WITHDRAWN'` |
| created_at | DateTimeField | Auto-set |

**`listings_bid` table**

| Field | Type | Notes |
|---|---|---|
| listing | FK -> Listing | CASCADE |
| bidder | FK -> User | CASCADE |
| amount | Decimal(12,2) | Bid amount |
| created_at | DateTimeField | Auto-set |

**`listings_searchlog` table** — Search keyword tracking for analytics

| Field | Type | Notes |
|---|---|---|
| keyword | CharField | Search term |
| created_at | DateTimeField | Auto-set |

**`listings_listingreport` table**

| Field | Type | Notes |
|---|---|---|
| reporter | FK -> User | CASCADE |
| listing | FK -> Listing | CASCADE |
| reason | CharField | `'fake'`, `'spam'`, `'inappropriate'`, `'sold'`, `'other'` |
| detail | TextField | Reporter's description |
| created_at | DateTimeField | Auto-set |
| | | `unique_together: (reporter, listing)` |

**`listings_searchalert` table**

| Field | Type | Notes |
|---|---|---|
| user | FK -> User | CASCADE |
| label | CharField | Alert name |
| query | CharField | Search keywords |
| category | FK -> Category | Optional filter |
| condition | CharField | Optional filter |
| max_price | Decimal | Optional filter |
| is_active | BooleanField | Paused / active |
| created_at | DateTimeField | Auto-set |

**`listings_userinteraction` table**

| Field | Type | Notes |
|---|---|---|
| user | FK -> User | CASCADE |
| listing | FK -> Listing | CASCADE |
| interaction_type | CharField | `'view'`, `'favorite'`, `'purchase'` |
| created_at | DateTimeField | Auto-set |
| | | `unique_together: (user, listing, interaction_type)` |

### 6.4 Orders App (6 models)

**`orders_order` table**

| Field | Type | Notes |
|---|---|---|
| listing | FK -> Listing | SET_NULL |
| buyer | FK -> User | CASCADE |
| seller | FK -> User | CASCADE |
| offer | FK -> Offer | SET_NULL, optional |
| total_amount | Decimal(12,2) | Final price paid |
| status | CharField | `'pending_payment'`, `'paid'`, `'shipped'`, `'delivered'`, `'cancelled'` |
| escrow_status | CharField | `'pending'`, `'held'`, `'released'`, `'refunded'`, `'disputed'` |
| tracking_number | CharField | Shipping tracking |
| delivered_at | DateTimeField | When buyer confirmed delivery |
| protection_expires_at | DateTimeField | When escrow auto-releases |
| created_at | DateTimeField | Auto-set |

**`orders_payment` table**

| Field | Type | Notes |
|---|---|---|
| order | OneToOne -> Order | CASCADE |
| stripe_payment_intent_id | CharField | Unique Stripe PI ID |
| amount | Decimal(12,2) | Amount charged |
| status | CharField | `'pending'`, `'succeeded'`, `'failed'`, `'refunded'` |
| created_at | DateTimeField | Auto-set |

**`orders_review` table**

| Field | Type | Notes |
|---|---|---|
| order | OneToOne -> Order | CASCADE |
| reviewer | FK -> User | Buyer who reviewed |
| seller | FK -> User | Seller being reviewed |
| rating | PositiveSmallInteger | 1-5 stars |
| comment | TextField | Review text |
| created_at | DateTimeField | Auto-set |

**`review_images` table**

| Field | Type | Notes |
|---|---|---|
| review | FK -> Review | CASCADE |
| image | ImageField | Review photo (Cloudinary) |
| created_at | DateTimeField | Auto-set |

**`orders_dispute` table**

| Field | Type | Notes |
|---|---|---|
| order | FK -> Order | CASCADE |
| opened_by | FK -> User | Who opened the dispute |
| reason | CharField | `'item_not_received'`, `'item_not_as_described'`, `'damaged'`, `'wrong_item'`, `'other'` |
| description | TextField | Detailed issue description |
| status | CharField | `'open'`, `'under_review'`, `'resolved_refund'`, `'resolved_no_refund'`, `'closed'` |
| resolution | TextField | Admin's resolution notes |
| created_at | DateTimeField | Auto-set |
| updated_at | DateTimeField | Auto-updated |

**`orders_receipt` table**

| Field | Type | Notes |
|---|---|---|
| order | OneToOne -> Order | CASCADE |
| issued_at | DateTimeField | Auto-set |
| pdf_url | CharField | Receipt download URL |

### 6.5 Messaging App (1 model)

**`messaging_message` table**

| Field | Type | Notes |
|---|---|---|
| sender | FK -> User | CASCADE |
| recipient | FK -> User | CASCADE |
| listing | FK -> Listing | SET_NULL, optional context |
| body | TextField | Message content |
| is_read | BooleanField | Default false |
| created_at | DateTimeField | Auto-set |

### 6.6 Notifications App (2 models)

**`notifications_notification` table**

| Field | Type | Notes |
|---|---|---|
| user | FK -> User | CASCADE |
| type | CharField | 14 types: `offer_received`, `outbid`, `auction_won`, `order_paid`, `order_shipped`, `order_delivered`, `new_bid`, `price_drop`, `review_received`, `dispute_opened`, `dispute_resolved`, `search_alert`, `listing_flagged`, `offer_accepted` |
| title | CharField | Notification title |
| message | TextField | Notification body |
| link | CharField | Frontend route to navigate |
| is_read | BooleanField | Default false |
| created_at | DateTimeField | Auto-set |

**`notifications_emaillog` table**

| Field | Type | Notes |
|---|---|---|
| recipient | EmailField | Email address |
| subject | CharField | Email subject |
| body | TextField | Email content |
| status | CharField | `'sent'` or `'failed'` |
| created_at | DateTimeField | Auto-set |

---

## 7. API Reference

### 7.1 Authentication (`/api/auth/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/register/` | Public | Create account (buyer/seller) with email verification |
| POST | `/login/` | Public | Login -> returns JWT tokens (rate limited: 5/min) |
| POST | `/token/refresh/` | Public | Refresh expired access token |
| GET | `/verify-email/?token=` | Public | Verify email with UUID token |
| POST | `/resend-verification/` | Public | Resend verification email |
| POST | `/password-reset/` | Public | Request password reset link |
| POST | `/password-reset/confirm/` | Public | Set new password with reset token |
| GET | `/me/` | Auth | Get current user profile |
| PATCH | `/me/` | Auth | Update profile (bio, phone, address, avatar) |

### 7.2 Two-Factor Authentication (`/api/auth/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/2fa/setup/` | Auth | Generate TOTP secret + QR code |
| POST | `/2fa/verify/` | Auth | Verify code to enable 2FA |
| POST | `/2fa/disable/` | Auth | Disable 2FA (requires valid TOTP code) |
| POST | `/login/2fa/` | Public | Complete login with username + password + TOTP code |

### 7.3 User Management (`/api/auth/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/sellers/<username>/` | Public | Seller profile with listings, reviews, avg rating |
| POST | `/users/<id>/block/` | Auth | Block a user |
| DELETE | `/users/<id>/unblock/` | Auth | Unblock a user |
| GET | `/blocked/` | Auth | List blocked users |
| GET | `/users/<id>/reputation/` | Auth | Buyer reputation score (based on dispute ratio) |

### 7.4 Admin Endpoints (`/api/auth/admin/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/users/` | Admin | List all users |
| PATCH | `/users/<id>/` | Admin | Update user (role, active, verified) |
| DELETE | `/users/<id>/` | Admin | Delete user |
| GET | `/listings/` | Admin | List all listings |
| DELETE | `/listings/<id>/` | Admin | Delete listing |
| GET | `/activity-logs/` | Admin | View activity logs (filterable by user_id) |

### 7.5 Listings (`/api/listings/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | Public | List listings with search, filters, pagination |
| POST | `/` | Seller | Create listing (rate limited: 10/hr, auto-moderated) |
| GET | `/<id>/` | Public | Listing detail |
| PUT/PATCH | `/<id>/` | Owner | Update listing (re-runs moderation) |
| DELETE | `/<id>/` | Owner | Delete listing |
| POST | `/<id>/images/` | Owner | Upload image (max 5 per listing) |
| DELETE | `/<id>/images/<img_id>/` | Owner | Delete image |
| GET | `/<id>/related/` | Public | 6 related listings (same category, similar price) |
| POST | `/<id>/buy/` | Buyer | Buy at listed price -> creates order |
| POST | `/<id>/favorite/` | Auth | Add to favorites |
| DELETE | `/<id>/favorite/` | Auth | Remove from favorites |
| GET | `/favorites/` | Auth | List favorited listings |
| POST | `/<id>/view/` | Auth | Log view interaction (analytics) |
| POST | `/<id>/contact/` | Auth | Send message to seller about listing |
| POST | `/<id>/report/` | Auth | Report listing (auto-hides at 3+ reports) |
| GET | `/categories/` | Public | List all categories |
| GET | `/my/` | Seller | Seller's own listings |
| POST | `/batch/` | Public | Fetch multiple listings by IDs |

### 7.6 Offers (`/api/listings/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/<id>/offers/` | Seller | View offers on listing |
| POST | `/<id>/offers/` | Buyer | Submit price offer (blocked users prevented) |
| PATCH | `/offers/<id>/` | Seller | Accept or reject offer |
| GET | `/my/offers/` | Seller | All offers on seller's listings |

### 7.7 Bids (`/api/listings/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/<id>/bids/` | Public | Bid history for auction listing |
| POST | `/<id>/bids/` | Buyer | Place bid (must exceed current highest) |
| POST | `/<id>/accept-bid/` | Seller | Accept top bid, create order |

### 7.8 Search Alerts (`/api/listings/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/search-alerts/` | Auth | List saved search alerts |
| POST | `/search-alerts/` | Auth | Create alert (query, category, condition, max_price) |
| PATCH | `/search-alerts/<id>/` | Auth | Toggle active/paused |
| DELETE | `/search-alerts/<id>/` | Auth | Delete alert |

### 7.9 Admin Reports (`/api/listings/admin/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/reports/` | Admin | List all listing reports |
| DELETE | `/reports/<id>/` | Admin | Dismiss a report |

### 7.10 Orders (`/api/orders/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | Auth | List orders (buyer sees purchases, seller sees sales) |
| GET | `/<id>/` | Auth | Order detail (buyer or seller only) |
| PATCH | `/<id>/status/` | Auth | Update status: seller -> `'shipped'`, buyer -> `'delivered'` |
| GET | `/<id>/shipping-label/` | Auth | Download PDF shipping label (4x6 inches) |
| POST | `/<id>/review/` | Buyer | Create review with rating, comment, photos (up to 3) |
| GET | `/seller/<id>/reviews/` | Public | Seller's reviews and average rating |
| GET | `/admin/stats/` | Admin | Platform statistics |

### 7.11 Disputes (`/api/orders/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/disputes/` | Auth | List disputes (admin sees all) |
| POST | `/disputes/` | Auth | Open dispute (freezes escrow) |
| GET | `/disputes/<id>/` | Auth | Dispute detail |
| PATCH | `/disputes/<id>/` | Auth/Admin | Resolve: refund, no refund, close, under review |

### 7.12 Payments (`/api/payments/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/create-intent/` | Auth | Create Stripe PaymentIntent for order |
| POST | `/confirm/` | Auth | Verify payment with Stripe after frontend confirmation |
| POST | `/webhook/` | Stripe | Webhook: `payment_intent.succeeded` / `payment_intent.payment_failed` |

### 7.13 Messaging (`/api/messages/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | Auth | List conversation threads (latest msg per partner) |
| GET | `/unread/` | Auth | Unread message count |
| GET | `/<partner_id>/` | Auth | Full conversation with a user |
| POST | `/<partner_id>/` | Auth | Send message |

### 7.14 Notifications (`/api/notifications/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | Auth | Last 50 notifications + unread count |
| POST | `/<id>/read/` | Auth | Mark notification as read |
| POST | `/read-all/` | Auth | Mark all as read |

### 7.15 Analytics (`/api/analytics/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/search-trends/` | Seller | Top 10 keywords, weekly search volume (7 weeks) |
| GET | `/revenue/` | Seller | Total revenue, listing counts, recent 5 orders |

### 7.16 Listing Search Query Parameters

| Param | Type | Description |
|---|---|---|
| `q` | string | Full-text search on title + description |
| `category` | slug | Filter by category |
| `condition` | string | `'new'`, `'used'`, `'refurbished'` |
| `min_price` | number | Minimum price |
| `max_price` | number | Maximum price |
| `listing_type` | string | `'auction'` or `'fixed'` |
| `sort` | string | `'newest'`, `'price_asc'`, `'price_desc'`, `'ending_soon'` |
| `page` | number | Page number (20 items per page) |

---

## 8. Frontend Application

### 8.1 Pages (23 total)

| Page | Route | Access | Purpose |
|---|---|---|---|
| Home | `/` | Public | Landing page, featured listings, categories, recently viewed |
| Login | `/login` | Public | Login with 2FA challenge support |
| Register | `/register` | Public | Signup with role selection (buyer/seller) |
| VerifyEmail | `/verify-email` | Public | Email verification with UUID token |
| ResetPassword | `/reset-password` | Public | Password reset (request + confirm) |
| Listings | `/listings` | Public | Browse/search/filter all active listings |
| ListingDetail | `/listings/:id` | Public | Full listing view, bid/offer/buy, share, report |
| SellerProfile | `/sellers/:username` | Public | Public seller page with reviews |
| Profile | `/profile` | Auth | Edit profile, manage 2FA |
| BuyerOrders | `/buyer/orders` | Buyer | Order table with escrow, review, dispute actions |
| BuyerFavorites | `/buyer/favorites` | Auth | Saved/favorited listings |
| Checkout | `/checkout/:orderId` | Auth | Stripe card payment with buyer protection info |
| OrderDetail | `/orders/:id` | Auth | Order progress tracker, review form |
| Inbox | `/inbox` | Auth | Direct messaging with conversation threads |
| DisputeCenter | `/disputes` | Auth | View/manage disputes |
| SearchAlerts | `/search-alerts` | Auth | Manage saved search alerts |
| SellerDashboard | `/seller/dashboard` | Seller | Revenue, charts, recent sales |
| SellerListings | `/seller/listings` | Seller | Manage all listings (table view) |
| CreateListing | `/seller/listings/new` | Seller | Create new listing form |
| EditListing | `/seller/listings/:id/edit` | Seller | Edit existing listing |
| SellerOffers | `/seller/offers` | Seller | View/accept/reject incoming offers |
| SellerOrders | `/seller/orders` | Seller | Sales table with shipping and escrow |
| SupportPanel | `/support` | Admin | Full admin panel (5 tabs) |

### 8.2 Reusable Components (6)

| Component | Purpose |
|---|---|
| Navbar | Header with role-based nav links, notification bell with badge, mobile hamburger menu |
| ListingCard | Listing card with image, price, condition badge, seller info, favorite button |
| ImageGallery | Main image with thumbnail strip navigation |
| BidForm | Auction bid input with current highest bid display and validation |
| OfferForm | Price offer input for negotiable listings |
| Countdown | Live countdown timer for auction end times (compact and full modes) |

### 8.3 SupportPanel Admin Tabs

| Tab | Features |
|---|---|
| Dashboard | Open disputes count, total disputes, reports, orders, users, active listings |
| Disputes | Table of all disputes, detail panel, resolve with refund/no-refund/close |
| Reports | Listing reports table, dismiss action |
| Users | Searchable user table, toggle verified/active, delete |
| Listings | Searchable listings table, delete action |
| Activity Logs | Login history with IP addresses, action type badges, timestamps |

---

## 9. Standard Operating Procedures

### 9.1 User Registration & Authentication

#### SOP-AUTH-001: New User Registration

**Procedure:**
1. User fills registration form (username, email, password, role: buyer/seller)
2. Frontend POSTs to `/api/auth/register/`
3. Backend validates input, hashes password with PBKDF2+SHA256
4. Creates user with `is_verified=false`
5. Generates UUID `verification_token`
6. Sends verification email via Brevo HTTP API with link: `{FRONTEND_URL}/verify-email?token={uuid}`
7. Logs activity: `action='register'`, records IP and user agent
8. User clicks email link -> frontend sends token to `/api/auth/verify-email/`
9. Backend sets `is_verified=true`, clears token
10. User can now log in

**Rate Limit:** 5 requests/minute per IP

#### SOP-AUTH-002: Standard Login

**Procedure:**
1. User submits username + password
2. Frontend POSTs to `/api/auth/login/`
3. Backend verifies credentials
4. If email not verified -> returns error "Please verify your email"
5. If 2FA enabled -> returns `{2fa_required: true}` error
6. If valid -> returns `{access, refresh, user}` (JWT tokens + user data)
7. Frontend stores tokens in `localStorage`, sets user in AuthContext
8. Logs activity: `action='login'` (or `'login_failed'`)

**Token Lifetimes:**
- Access token: 1 day
- Refresh token: 30 days
- Refresh tokens are rotated on use

#### SOP-AUTH-003: Token Refresh

**Procedure:**
1. API request returns 401 (access token expired)
2. Axios interceptor catches the error
3. Sends refresh token to `/api/auth/token/refresh/`
4. Receives new access token
5. Stores new token, retries original request
6. If refresh also expired -> clears tokens, redirects to `/login`

#### SOP-AUTH-004: Password Reset

**Procedure:**
1. User submits email to `/api/auth/password-reset/`
2. Backend generates UUID `password_reset_token`, records timestamp
3. Sends email with reset link: `{FRONTEND_URL}/reset-password?token={uuid}`
4. User clicks link, enters new password
5. Frontend POSTs token + new password to `/api/auth/password-reset/confirm/`
6. Backend verifies token exists and is less than 24 hours old
7. Updates password, clears token

---

### 9.2 Listing Management

#### SOP-LIST-001: Creating a Listing

**Procedure:**
1. Seller fills form (title, description, price, condition, category, listing type)
2. Frontend POSTs to `/api/listings/`
3. Backend verifies `user.role == 'seller'`
4. Content moderation runs automatically:
   - Checks title/description against banned keywords list
   - Checks if price is below suspicious threshold ($1 CAD)
   - If flagged: sets `is_flagged=true` with reason
5. Listing created with status `'active'` (or `'draft'` if selected)
6. Frontend uploads images (up to 5) via `/api/listings/{id}/images/`
7. Each image is uploaded to Cloudinary and URL stored in database
8. If search alerts match the new listing -> notifications sent to alert owners

**Rate Limit:** 10 listings/hour per user

#### SOP-LIST-002: Auction Lifecycle

**Procedure:**
1. Seller creates listing with `auction_end_time` set
2. Buyers place bids -> each bid must exceed current highest
3. When `auction_end_time` passes:
   - Management command `settle_auctions` runs (cron: every hour)
   - Finds all expired active auctions with bids
   - Gets the highest bid
   - Creates Order for the winner
   - Sends notification and email to winner and seller
4. Alternatively: seller can manually accept highest bid early via `accept-bid` endpoint

---

### 9.3 Purchase & Payment Processing

#### SOP-PAY-001: Buy Now Flow

**Procedure:**
1. Buyer clicks "Buy Now" on a fixed-price listing
2. Frontend POSTs to `/api/listings/{id}/buy/`
3. Backend (inside `transaction.atomic()`):
   - Acquires row lock on listing (`select_for_update()`)
   - Verifies: listing is active, buyer is not the seller, buyer is not blocked
   - Sets listing status to `'sold'`
   - Creates Order with `status='pending_payment'`
   - Creates Stripe PaymentIntent (`amount` in cents, `currency='cad'`)
   - Creates Payment record
4. Returns `{order_id, client_secret}` to frontend
5. Frontend redirects to `/checkout/{order_id}`
6. Checkout page renders Stripe `<CardElement>` (secure iframe)
7. User enters card details, clicks Pay
8. `stripe.confirmCardPayment(client_secret)` sends card directly to Stripe
9. On success: frontend calls `/api/payments/confirm/` with `order_id`
10. Backend retrieves PaymentIntent from Stripe, verifies `status == 'succeeded'`
11. Updates: `payment.status='succeeded'`, `order.status='paid'`, `order.escrow_status='held'`
12. Creates receipt, sends notifications and emails to both parties

**Concurrency Protection:** `select_for_update()` prevents two buyers purchasing the same item simultaneously.

#### SOP-PAY-002: Offer Acceptance Payment

**Procedure:**
1. Seller accepts offer via `/api/listings/offers/{id}/` with `status='ACCEPTED'`
2. Backend (inside `transaction.atomic()`):
   - Marks listing as `'sold'`
   - Rejects all other pending offers
   - Creates Order with offer amount
   - Creates Stripe PaymentIntent
3. Buyer receives notification with link to checkout
4. Payment flow continues as SOP-PAY-001 steps 5-12

#### SOP-PAY-003: Handling Already-Succeeded Payments

**Procedure:**
If a user returns to checkout for an order whose PaymentIntent already succeeded (e.g., browser closed mid-flow):
1. `/api/payments/create-intent/` retrieves existing PaymentIntent from Stripe
2. If `intent.status == 'succeeded'`: auto-confirms order, returns `{already_paid: true}`
3. If `intent.status` is still usable: returns existing `client_secret`
4. If `intent.status` is terminal/failed: deletes old payment, creates fresh PaymentIntent

---

### 9.4 Escrow & Buyer Protection

#### SOP-ESC-001: Escrow Lifecycle

```
Payment Succeeds:
  -> escrow_status = 'held' (funds held)

Seller Ships:
  -> order.status = 'shipped'
  -> Tracking number saved
  -> Buyer notified via email and in-app notification

Buyer Confirms Delivery:
  -> order.status = 'delivered'
  -> order.delivered_at = now
  -> order.protection_expires_at = now + 7 days
  -> Both parties notified

Protection Period (7 days):
  -> Buyer can open a dispute
  -> Escrow remains 'held'

If Dispute Opened:
  -> escrow_status = 'disputed' (frozen)
  -> See SOP-DIS-001

If No Dispute After 7 Days:
  -> Management command: release_escrow
  -> escrow_status = 'released'
  -> Both parties notified

Escrow Status Flow:
  pending -> held -> released (normal)
  pending -> held -> disputed -> refunded (buyer wins dispute)
  pending -> held -> disputed -> released (seller wins dispute)
```

---

### 9.5 Dispute Resolution

#### SOP-DIS-001: Opening a Dispute

**Procedure:**
1. Buyer or seller opens dispute via `/api/orders/disputes/` with reason and description
2. Reasons: `item_not_received`, `item_not_as_described`, `damaged`, `wrong_item`, `other`
3. If escrow is `'held'` -> status changes to `'disputed'` (frozen)
4. Other party notified
5. Duplicate disputes on the same order are prevented

#### SOP-DIS-002: Admin Resolution

**Procedure:**
1. Admin reviews dispute in Support Panel
2. Resolution options:
   - **Under Review**: marks as being investigated
   - **Resolved — Refund**: issues Stripe refund (`stripe.Refund.create()`), sets `payment.status='refunded'`, `escrow_status='refunded'` (wrapped in `transaction.atomic()`)
   - **Resolved — No Refund**: releases escrow to seller
   - **Closed**: releases escrow to seller
3. Both parties notified of resolution

---

### 9.6 Content Moderation

#### SOP-MOD-001: Automated Listing Screening

**Trigger:** Every listing create and edit operation.

**Procedure:**
1. `check_listing()` runs against title and description
2. Checks banned keyword list: counterfeit, replica, fake designer, knockoff, stolen, drugs, weapons, illegal
3. Checks price threshold: listings below $1 CAD flagged as suspicious
4. If match found: `is_flagged=true`, `flagged_reason` set
5. Flagged listings appear in admin Support Panel

#### SOP-MOD-002: User Report Escalation

**Procedure:**
1. User reports listing with reason (fake, spam, inappropriate, sold, other)
2. Each user can only report a listing once (`unique_together`)
3. At 3+ reports: listing auto-hidden (`status='closed'`), seller notified
4. Admin can review reports in Support Panel and dismiss or take action

---

### 9.7 Two-Factor Authentication

#### SOP-2FA-001: Setup

**Procedure:**
1. User requests 2FA setup via `/api/auth/2fa/setup/`
2. Backend generates random TOTP secret with `pyotp.random_base32()`
3. Stores secret in `User.totp_secret`
4. Generates QR code from provisioning URI, encodes as base64 PNG
5. Returns QR code + secret to frontend
6. User scans QR with authenticator app (Google Authenticator / Authy)
7. User enters 6-digit code from app to `/api/auth/2fa/verify/`
8. Backend verifies code with `pyotp.TOTP(secret).verify(code, valid_window=1)`
9. Sets `is_2fa_enabled=true`
10. Logs activity: `action='2fa_enabled'`

#### SOP-2FA-002: Login with 2FA

**Procedure:**
1. Standard login attempt returns `{2fa_required: true}` error
2. Frontend shows TOTP code input
3. User enters 6-digit code from authenticator app
4. Frontend POSTs username + password + code to `/api/auth/login/2fa/`
5. Backend verifies credentials then verifies TOTP code
6. If valid: returns JWT tokens + user data
7. If invalid code: returns error

---

## 10. Security Policies

### 10.1 Rate Limiting

| Scope | Limit | Applied To |
|---|---|---|
| Anonymous | 60/minute | All unauthenticated requests |
| Authenticated | 120/minute | All authenticated requests |
| Auth (login/register) | 5/minute | Login, register, 2FA login |
| Listing Creation | 10/hour | Creating new listings |

### 10.2 Authentication Security

- Passwords hashed with PBKDF2 + SHA256 (Django default) — never stored in plaintext
- JWT tokens signed with `SECRET_KEY` — tampered tokens are rejected
- Refresh token rotation enabled — old refresh tokens invalidated
- Email verification required before login
- Password reset tokens expire after 24 hours

### 10.3 Payment Security (PCI Compliance)

- Card details never touch our server — Stripe.js sends them directly to Stripe via secure iframe
- We only handle PaymentIntent IDs
- Payment verification: after frontend payment, backend verifies with Stripe API before updating order
- Webhook signature verification: Stripe signs events, we verify using `STRIPE_WEBHOOK_SECRET`
- Dual confirmation: frontend `/confirm/` endpoint + Stripe webhook (belt and suspenders)

### 10.4 Cross-Origin Security

- `CORS_ALLOWED_ORIGINS` whitelist — only specific frontend URLs accepted
- JWT sent via `Authorization` header (not cookies) — immune to CSRF
- Stripe webhook uses `@csrf_exempt` with cryptographic signature verification

### 10.5 Input Validation

- React auto-escapes all rendered content — prevents XSS
- Django ORM uses parameterized queries — prevents SQL injection
- Serializer validation on all incoming API data
- File type validation on image uploads (Pillow)

### 10.6 User Blocking

- Blocked users cannot: make offers, buy listings from the blocker, or bid on the blocker's auctions
- Block check enforced at transaction points (`buy_now`, `offer creation`)
- Bidirectional lookup: `BlockedUser.objects.filter(blocker=seller, blocked=buyer).exists()`

### 10.7 Activity Logging

- Tracks: login, login_failed, register, password_reset, profile_update, 2fa_enabled, 2fa_disabled
- Records: IP address (from `X-Forwarded-For`), user agent, timestamp
- Viewable by admin in Support Panel Activity Logs tab

---

## 11. Deployment Procedures

### 11.1 Backend Deployment (Render)

**Platform:** Render Web Service

**Configuration:**
- Repository: `github.com/jilspatel1412/SellIT`
- Root Directory: `backend`
- Runtime: Python 3
- Build Command: `./build.sh`
- Start Command: `gunicorn sellit.wsgi --log-file -`

**Build Script (`build.sh`) executes:**
1. `pip install -r requirements.txt` — install Python packages
2. `python manage.py collectstatic --noinput` — gather static files for WhiteNoise
3. `python manage.py migrate` — apply database migrations
4. `python manage.py create_admin` — create admin account from environment variables

**Database:** Render Managed PostgreSQL (connected via `DATABASE_URL`)

### 11.2 Frontend Deployment (Vercel)

**Platform:** Vercel

**Configuration:**
- Repository: `github.com/jilspatel1412/SellIT`
- Framework: Vite
- Root Directory: `frontend`
- Build Command: `npm install && npm run build`
- Output Directory: `dist`
- SPA Routing: `vercel.json` rewrites all paths to `index.html`

### 11.3 Stripe Webhook Setup

1. Stripe Dashboard -> Webhooks -> Add endpoint
2. URL: `https://sellit-ma71.onrender.com/api/payments/webhook/`
3. Events: `payment_intent.succeeded`, `payment_intent.payment_failed`
4. Copy signing secret -> set as `STRIPE_WEBHOOK_SECRET` on Render

### 11.4 Auto-Deployment

Both Render and Vercel are connected to the GitHub repository. Pushing to the `main` branch automatically triggers builds and deployments on both platforms.

---

## 12. Environment Configuration

### 12.1 Backend Environment Variables (Render)

| Variable | Description | Required |
|---|---|---|
| `SECRET_KEY` | Django secret key (random 50-char string) | Yes |
| `DEBUG` | `False` for production | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `ALLOWED_HOSTS` | Backend hostname | Yes |
| `FRONTEND_URL` | Frontend origin URL | Yes |
| `CORS_ALLOWED_ORIGINS` | Comma-separated allowed frontend origins | Yes |
| `STRIPE_SECRET_KEY` | Stripe secret key (`sk_test_...`) | Yes |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret (`whsec_...`) | Yes |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | Yes |
| `CLOUDINARY_API_KEY` | Cloudinary API key | Yes |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | Yes |
| `BREVO_API_KEY` | Brevo API key for transactional emails | Yes |
| `DEFAULT_FROM_EMAIL` | Sender email address | Yes |
| `ADMIN_USERNAME` | Auto-created admin username | For auto-create |
| `ADMIN_EMAIL` | Auto-created admin email | For auto-create |
| `ADMIN_PASSWORD` | Auto-created admin password | For auto-create |

### 12.2 Frontend Environment Variables (Vercel)

| Variable | Description | Required |
|---|---|---|
| `VITE_API_BASE_URL` | Backend API URL | Yes |
| `VITE_STRIPE_PUBLISHABLE_KEY` | Stripe publishable key (`pk_test_...`) | Yes |

### 12.3 Test Cards (Stripe Test Mode)

| Card Number | Result |
|---|---|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 0002` | Card declined |

Use any future expiry date and any 3-digit CVC.

---

## 13. Scheduled Maintenance Tasks

| Command | Purpose | Schedule |
|---|---|---|
| `python manage.py migrate` | Apply database migrations | Auto on deploy |
| `python manage.py create_admin` | Create admin user from env vars | Auto on deploy |
| `python manage.py seed_categories` | Seed 12 default product categories | Auto via data migration |
| `python manage.py settle_auctions` | Close expired auctions, create orders, notify winners | Cron: every hour |
| `python manage.py release_escrow` | Release held escrow after 7-day protection period | Cron: daily |

---

## 14. Software Development Lifecycle

### 14.1 Methodology: Agile (Scrum)

We followed the Agile (Scrum) methodology, building the project in iterative sprints of 1-2 weeks each. Requirements were refined incrementally based on testing and feedback.

### 14.2 Sprint Breakdown

| Sprint | Duration | Deliverable |
|---|---|---|
| Sprint 1 | Week 1-2 | User auth — registration, login, email verification, JWT tokens |
| Sprint 2 | Week 3-4 | Listings — create, edit, delete, image upload via Cloudinary |
| Sprint 3 | Week 5 | Browse & Search — listing page, filters, categories, search logs |
| Sprint 4 | Week 6 | Offers & Bidding — make offer, counter-offer, accept/reject, auction bidding |
| Sprint 5 | Week 7-8 | Payments — Stripe integration, escrow system, checkout flow |
| Sprint 6 | Week 8-9 | Orders — order tracking, shipping labels, delivery confirmation |
| Sprint 7 | Week 9-10 | Messaging — direct inbox, conversation threads |
| Sprint 8 | Week 10-11 | Admin & Moderation — support panel, content moderation, dispute resolution |
| Sprint 9 | Week 11-12 | Advanced features — 2FA, search alerts, favorites, analytics dashboard |
| Sprint 10 | Week 12-13 | Deployment & Polish — Render + Vercel, CORS config, bug fixes, security hardening |

### 14.3 Why Agile

- **Early delivery**: After Sprint 3, we had a functional browsing experience
- **Adaptability**: When we realized admin should be a pure moderator (not buyer/seller), we pivoted in one sprint
- **Risk management**: Stripe integration was tackled in Sprint 5 (not last) to allow time for debugging
- **Early bug detection**: Payment status bug was caught in Sprint 5 testing, not at the end

### 14.4 Agile vs Waterfall

| Aspect | Waterfall | Agile (SellIt) |
|---|---|---|
| Planning | All upfront | Sprint by sprint |
| Delivery | One final release | Working app after each sprint |
| Change handling | Expensive rework | Add to next sprint backlog |
| Testing | After all development | Every sprint |
| Client feedback | At the end | After every sprint |
| Risk | High (problems found late) | Low (problems found early) |

---


*End of Document*
