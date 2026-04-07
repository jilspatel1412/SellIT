# SellIt — Complete Project Study

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Architecture](#3-architecture)
4. [Database Schema](#4-database-schema)
5. [Backend API Reference](#5-backend-api-reference)
6. [Frontend Pages & Components](#6-frontend-pages--components)
7. [Authentication Flow](#7-authentication-flow)
8. [Payment Flow](#8-payment-flow)
9. [Escrow & Buyer Protection](#9-escrow--buyer-protection)
10. [Safety & Security Features](#10-safety--security-features)
11. [Deployment Guide](#11-deployment-guide)
12. [Environment Variables](#12-environment-variables)
13. [Team Contributions](#13-team-contributions)

---

## 1. Project Overview

SellIt is a full-stack peer-to-peer marketplace where users can buy and sell items with built-in safety features. It supports fixed-price listings and auctions, Stripe payments with escrow protection, two-factor authentication, content moderation, and a full admin panel.

**Live URLs:**
- Frontend: Vercel (React + Vite)
- Backend: Render (Django REST Framework + PostgreSQL)

**Key Capabilities:**
- User registration with email verification and role selection (buyer/seller)
- Listings with multiple images, categories, search/filter, and auction support
- Offer/negotiate system for fixed-price listings
- Bidding system for auction listings
- Stripe payment processing with escrow hold
- 7-day buyer protection period after delivery
- Dispute resolution with admin panel
- Two-factor authentication (TOTP)
- Direct messaging between users
- In-app and email notifications
- Seller analytics dashboard
- Content moderation and report auto-escalation
- Rate limiting, user blocking, activity logging

---

## 2. Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Django 5.0 | Web framework |
| Django REST Framework 3.16 | REST API |
| PostgreSQL | Database (via dj-database-url) |
| SimpleJWT | JWT authentication (access + refresh tokens) |
| Stripe 14.4 | Payment processing |
| Cloudinary | Image storage (listings, avatars, reviews) |
| PyOTP 2.9 + qrcode 8.2 | TOTP-based two-factor authentication |
| ReportLab 4.2 | PDF generation (shipping labels) |
| Brevo HTTP API | Transactional emails (production) |
| Gunicorn | WSGI server |
| WhiteNoise | Static file serving |

### Frontend
| Technology | Purpose |
|---|---|
| React 18.3 | UI library |
| Vite 5.3 | Build tool and dev server |
| React Router 6.26 | Client-side routing |
| Axios 1.7 | HTTP client with JWT interceptors |
| Stripe.js 4.0 + React Stripe 2.7 | Payment UI |
| Recharts 2.12 | Charts for seller analytics |

### Infrastructure
| Service | Purpose |
|---|---|
| Render | Backend hosting + PostgreSQL database |
| Vercel | Frontend hosting with SPA routing |
| Cloudinary | CDN for uploaded images |
| Stripe | Payment gateway |
| Brevo | Email delivery |

---

## 3. Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (Vercel)                     │
│  React + Vite SPA                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │  Pages   │ │Components│ │  Context  │ │ API Layer│   │
│  │ (23 pgs) │ │(6 shared)│ │(AuthCtx)  │ │ (Axios)  │   │
│  └──────────┘ └──────────┘ └──────────┘ └────┬─────┘   │
└──────────────────────────────────────────────┬──────────┘
                                               │ HTTPS/JWT
┌──────────────────────────────────────────────┴──────────┐
│                   BACKEND (Render)                       │
│  Django REST Framework                                   │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐           │
│  │ Users  │ │Listings│ │ Orders │ │  Msgs  │           │
│  │  App   │ │  App   │ │  App   │ │  App   │           │
│  └────────┘ └────────┘ └────────┘ └────────┘           │
│  ┌────────────┐ ┌────────────┐                          │
│  │Notifications│ │ Analytics  │                          │
│  │    App      │ │    App     │                          │
│  └──────┬──────┘ └────────────┘                          │
└─────────┼────────────────────────────────────────────────┘
          │
    ┌─────┴─────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
    │ PostgreSQL│  │Cloudinary│  │  Stripe  │  │ Brevo  │
    │    (DB)   │  │ (Images) │  │(Payments)│  │(Emails)│
    └───────────┘  └──────────┘  └──────────┘  └────────┘
```

### Backend Apps

| App | Responsibility |
|---|---|
| `users` | Authentication, profiles, 2FA, blocking, activity logs, admin user management |
| `listings` | Listings CRUD, images, categories, offers, bids, auctions, search, favorites, reports, moderation |
| `orders` | Orders, Stripe payments, escrow, shipping labels, reviews, disputes, receipts |
| `messaging` | Direct messages between users, conversation threads |
| `notifications` | In-app notifications, email sending via Brevo/SMTP |
| `analytics` | Seller revenue dashboard, search trend tracking |

---

## 4. Database Schema

### Users App

**`users` table** (Custom User — extends AbstractUser)
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| username | CharField | Unique |
| email | EmailField | Unique |
| password | CharField | Hashed |
| role | CharField | 'buyer', 'seller', or 'admin' |
| is_verified | Boolean | Email verified (default: false) |
| avatar | ImageField | Profile picture (Cloudinary) |
| bio | TextField | User bio |
| phone_number | CharField | Unique, optional |
| address_line1 | CharField | Street address |
| city | CharField | City |
| state_province | CharField | Province/state |
| postal_code | CharField | Postal/zip code |
| country | CharField | Country |
| is_verified_seller | Boolean | Admin-granted seller badge |
| verification_token | UUIDField | For email verification link |
| password_reset_token | UUIDField | For password reset link |
| password_reset_requested_at | DateTimeField | Expiry tracking |
| totp_secret | CharField(64) | TOTP secret for 2FA |
| is_2fa_enabled | Boolean | Whether 2FA is active |
| date_joined | DateTimeField | Auto-set on creation |

**`activity_logs` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| user | FK → User | CASCADE |
| action | CharField | 'login', 'login_failed', 'register', 'password_reset', 'profile_update', '2fa_enabled', '2fa_disabled' |
| ip_address | GenericIPAddress | Client IP (from X-Forwarded-For) |
| user_agent | CharField(500) | Browser user agent |
| created_at | DateTimeField | Auto-set |

**`blocked_users` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| blocker | FK → User | Who blocked |
| blocked | FK → User | Who got blocked |
| created_at | DateTimeField | Auto-set |
| | | unique_together: (blocker, blocked) |

### Listings App

**`listings_category` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| name | CharField | Unique (e.g., "Electronics") |
| slug | SlugField | Unique, URL-safe |
| icon | CharField | Emoji or icon code |

**`listings_listing` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| seller | FK → User | CASCADE |
| category | FK → Category | SET_NULL, optional |
| title | CharField | Listing title |
| description | TextField | Full description |
| price | Decimal(12,2) | Price in CAD |
| is_negotiable | Boolean | Accepts offers? |
| condition | CharField | 'new', 'used', 'refurbished' |
| status | CharField | 'draft', 'active', 'sold', 'closed' (indexed) |
| auction_end_time | DateTimeField | Null if fixed-price |
| current_bid | Decimal(12,2) | Highest bid (null if no bids) |
| is_flagged | Boolean | Content moderation flag |
| flagged_reason | CharField(255) | Why it was flagged |
| created_at | DateTimeField | Auto-set (indexed) |
| updated_at | DateTimeField | Auto-updated |

**`listings_listingimage` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| listing | FK → Listing | CASCADE |
| image | ImageField | Cloudinary upload |
| url | URLField | Direct URL |
| order | PositiveInteger | Display order |

**`listings_offer` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| listing | FK → Listing | CASCADE |
| buyer | FK → User | CASCADE |
| offer_price | Decimal(12,2) | Offered price |
| status | CharField | 'PENDING', 'ACCEPTED', 'REJECTED', 'WITHDRAWN' |
| created_at | DateTimeField | Auto-set |

**`listings_bid` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| listing | FK → Listing | CASCADE |
| bidder | FK → User | CASCADE |
| amount | Decimal(12,2) | Bid amount |
| created_at | DateTimeField | Auto-set |

**`listings_searchlog` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| keyword | CharField | Search term |
| created_at | DateTimeField | Auto-set |

**`listings_listingreport` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| reporter | FK → User | CASCADE |
| listing | FK → Listing | CASCADE |
| reason | CharField | 'fake', 'spam', 'inappropriate', 'sold', 'other' |
| detail | TextField | Reporter's description |
| created_at | DateTimeField | Auto-set |
| | | unique_together: (reporter, listing) |

**`listings_searchalert` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| user | FK → User | CASCADE |
| label | CharField | Alert name |
| query | CharField | Search keywords |
| category | FK → Category | Optional filter |
| condition | CharField | Optional filter |
| max_price | Decimal | Optional filter |
| is_active | Boolean | Paused/active |
| created_at | DateTimeField | Auto-set |

**`listings_userinteraction` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| user | FK → User | CASCADE |
| listing | FK → Listing | CASCADE |
| interaction_type | CharField | 'view', 'favorite', 'purchase' |
| created_at | DateTimeField | Auto-set |
| | | unique_together: (user, listing, interaction_type) |

### Orders App

**`orders_order` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| listing | FK → Listing | SET_NULL |
| buyer | FK → User | CASCADE |
| seller | FK → User | CASCADE |
| offer | FK → Offer | SET_NULL, optional |
| total_amount | Decimal(12,2) | Final price paid |
| status | CharField | 'pending_payment', 'paid', 'shipped', 'delivered', 'cancelled' |
| escrow_status | CharField | 'pending', 'held', 'released', 'refunded', 'disputed' |
| tracking_number | CharField | Shipping tracking |
| delivered_at | DateTimeField | When buyer confirmed delivery |
| protection_expires_at | DateTimeField | When escrow auto-releases |
| created_at | DateTimeField | Auto-set |

**`orders_payment` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| order | OneToOne → Order | CASCADE |
| stripe_payment_intent_id | CharField | Unique Stripe PI ID |
| amount | Decimal(12,2) | Amount charged |
| status | CharField | 'pending', 'succeeded', 'failed' |
| created_at | DateTimeField | Auto-set |

**`orders_review` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| order | OneToOne → Order | CASCADE |
| reviewer | FK → User | Buyer who reviewed |
| seller | FK → User | Seller being reviewed |
| rating | PositiveSmallInteger | 1–5 stars |
| comment | TextField | Review text |
| created_at | DateTimeField | Auto-set |

**`review_images` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| review | FK → Review | CASCADE |
| image | ImageField | Review photo (Cloudinary) |
| created_at | DateTimeField | Auto-set |

**`orders_dispute` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| order | FK → Order | CASCADE |
| opened_by | FK → User | Who opened the dispute |
| reason | CharField | 'item_not_received', 'item_not_as_described', 'damaged', 'wrong_item', 'other' |
| description | TextField | Detailed issue description |
| status | CharField | 'open', 'under_review', 'resolved_refund', 'resolved_no_refund', 'closed' |
| resolution | TextField | Admin's resolution notes |
| created_at | DateTimeField | Auto-set |
| updated_at | DateTimeField | Auto-updated |

**`orders_receipt` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| order | OneToOne → Order | CASCADE |
| issued_at | DateTimeField | Auto-set |
| pdf_url | CharField | Receipt download URL |

### Messaging App

**`messaging_message` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| sender | FK → User | CASCADE |
| recipient | FK → User | CASCADE |
| listing | FK → Listing | SET_NULL, optional context |
| body | TextField | Message content |
| is_read | Boolean | Default false |
| created_at | DateTimeField | Auto-set |

### Notifications App

**`notifications_notification` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| user | FK → User | CASCADE |
| type | CharField | 14 types (offer_received, outbid, auction_won, order_paid, order_shipped, order_delivered, new_bid, price_drop, review_received, dispute_opened, dispute_resolved, search_alert, listing_flagged, offer_accepted) |
| title | CharField | Notification title |
| message | TextField | Notification body |
| link | CharField | Frontend route to navigate |
| is_read | Boolean | Default false |
| created_at | DateTimeField | Auto-set |

**`notifications_emaillog` table**
| Field | Type | Notes |
|---|---|---|
| id | AutoField | Primary key |
| recipient | EmailField | Email address |
| subject | CharField | Email subject |
| body | TextField | Email content |
| status | CharField | 'sent' or 'failed' |
| created_at | DateTimeField | Auto-set |

---

## 5. Backend API Reference

### Authentication (`/api/auth/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/register/` | Public | Create account (buyer/seller) with email verification |
| POST | `/login/` | Public | Login → returns JWT tokens (rate limited: 5/min) |
| POST | `/token/refresh/` | Public | Refresh expired access token |
| GET | `/verify-email/?token=` | Public | Verify email with UUID token |
| POST | `/resend-verification/` | Public | Resend verification email |
| POST | `/password-reset/` | Public | Request password reset link |
| POST | `/password-reset/confirm/` | Public | Set new password with reset token |
| GET | `/me/` | Auth | Get current user profile |
| PATCH | `/me/` | Auth | Update profile (bio, phone, address, avatar) |

### Two-Factor Authentication (`/api/auth/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/2fa/setup/` | Auth | Generate TOTP secret + QR code |
| POST | `/2fa/verify/` | Auth | Verify code to enable 2FA |
| POST | `/2fa/disable/` | Auth | Disable 2FA (requires valid TOTP code) |
| POST | `/login/2fa/` | Public | Complete login with username + password + TOTP code |

### User Management (`/api/auth/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/sellers/<username>/` | Public | Seller profile with listings, reviews, avg rating |
| POST | `/users/<id>/block/` | Auth | Block a user |
| DELETE | `/users/<id>/unblock/` | Auth | Unblock a user |
| GET | `/blocked/` | Auth | List blocked users |
| GET | `/users/<id>/reputation/` | Auth | Buyer reputation score (based on dispute ratio) |

### Admin (`/api/auth/admin/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/users/` | Admin | List all users |
| PATCH | `/users/<id>/` | Admin | Update user (role, active, verified) |
| DELETE | `/users/<id>/` | Admin | Delete user |
| GET | `/listings/` | Admin | List all listings |
| DELETE | `/listings/<id>/` | Admin | Delete listing |
| GET | `/activity-logs/` | Admin | View activity logs (filterable by user_id) |

### Listings (`/api/listings/`)

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
| POST | `/<id>/buy/` | Buyer | Buy at listed price → creates order |
| POST | `/<id>/favorite/` | Auth | Add to favorites |
| DELETE | `/<id>/favorite/` | Auth | Remove from favorites |
| GET | `/favorites/` | Auth | List favorited listings |
| POST | `/<id>/view/` | Auth | Log view interaction (analytics) |
| POST | `/<id>/contact/` | Auth | Send message to seller about listing |
| POST | `/<id>/report/` | Auth | Report listing (auto-hides at 3+ reports) |
| GET | `/categories/` | Public | List all categories |
| GET | `/my/` | Seller | Seller's own listings |
| POST | `/batch/` | Public | Fetch multiple listings by IDs |

### Offers (`/api/listings/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/<id>/offers/` | Seller | View offers on listing |
| POST | `/<id>/offers/` | Buyer | Submit price offer (blocked users prevented) |
| PATCH | `/offers/<id>/` | Seller | Accept or reject offer |
| GET | `/my/offers/` | Seller | All offers on seller's listings |

### Bids (`/api/listings/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/<id>/bids/` | Public | Bid history for auction listing |
| POST | `/<id>/bids/` | Buyer | Place bid (must exceed current highest) |
| POST | `/<id>/accept-bid/` | Seller | Accept top bid, create order |

### Search Alerts (`/api/listings/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/search-alerts/` | Auth | List saved search alerts |
| POST | `/search-alerts/` | Auth | Create alert (query, category, condition, max_price) |
| PATCH | `/search-alerts/<id>/` | Auth | Toggle active/paused |
| DELETE | `/search-alerts/<id>/` | Auth | Delete alert |

### Admin Reports (`/api/listings/admin/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/reports/` | Admin | List all listing reports |
| DELETE | `/reports/<id>/` | Admin | Dismiss a report |

### Orders (`/api/orders/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | Auth | List orders (buyer sees purchases, seller sees sales) |
| GET | `/<id>/` | Auth | Order detail (buyer or seller only) |
| PATCH | `/<id>/status/` | Auth | Update status: seller → 'shipped', buyer → 'delivered' |
| GET | `/<id>/shipping-label/` | Auth | Download PDF shipping label (4×6 inches) |
| POST | `/<id>/review/` | Buyer | Create review with rating, comment, photos (up to 3) |
| GET | `/seller/<id>/reviews/` | Public | Seller's reviews and average rating |
| GET | `/admin/stats/` | Admin | Platform statistics |

### Disputes (`/api/orders/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/disputes/` | Auth | List disputes (admin sees all) |
| POST | `/disputes/` | Auth | Open dispute (freezes escrow) |
| GET | `/disputes/<id>/` | Auth | Dispute detail |
| PATCH | `/disputes/<id>/` | Auth/Admin | Resolve: refund, no refund, close, under review |

### Payments (`/api/payments/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/create-intent/` | Auth | Create Stripe PaymentIntent for order |
| POST | `/webhook/` | Stripe | Webhook: payment_intent.succeeded / failed |

### Messaging (`/api/messages/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | Auth | List conversation threads (latest msg per partner) |
| GET | `/unread/` | Auth | Unread message count |
| GET | `/<partner_id>/` | Auth | Full conversation with a user |
| POST | `/<partner_id>/` | Auth | Send message |

### Notifications (`/api/notifications/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | Auth | Last 50 notifications + unread count |
| POST | `/<id>/read/` | Auth | Mark notification as read |
| POST | `/read-all/` | Auth | Mark all as read |

### Analytics (`/api/analytics/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/search-trends/` | Seller | Top 10 keywords, weekly search volume (7 weeks) |
| GET | `/revenue/` | Seller | Total revenue, listing counts, recent 5 orders |

### Query Parameters for Listing Search

| Param | Type | Description |
|---|---|---|
| `q` | string | Full-text search on title + description |
| `category` | slug | Filter by category |
| `condition` | string | 'new', 'used', 'refurbished' |
| `min_price` | number | Minimum price |
| `max_price` | number | Maximum price |
| `listing_type` | string | 'auction' or 'fixed' |
| `sort` | string | 'newest', 'price_asc', 'price_desc', 'ending_soon' |
| `page` | number | Page number (20 items per page) |

---

## 6. Frontend Pages & Components

### Pages (23 total)

| Page | Route | Role | Purpose |
|---|---|---|---|
| Home | `/` | Public | Landing page, featured listings, categories, recently viewed |
| Login | `/login` | Public | Login with 2FA challenge support |
| Register | `/register` | Public | Signup with role selection (buyer/seller) |
| VerifyEmail | `/verify-email` | Public | Email verification with token |
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

### Reusable Components (6)

| Component | Props | Purpose |
|---|---|---|
| Navbar | — (uses AuthContext) | Header with nav links, notification bell, mobile menu |
| ListingCard | `listing` | Card with image, price, condition, seller info |
| ImageGallery | `images` | Main image + thumbnail strip |
| BidForm | `listing`, `onBidPlaced` | Auction bid input with validation |
| OfferForm | `listing`, `onOfferSubmitted` | Price offer input for negotiable listings |
| Countdown | `endTime`, `compact`, `onExpire` | Live countdown timer for auctions |

### SupportPanel Admin Tabs

| Tab | Features |
|---|---|
| Disputes | Table of all disputes, detail panel, resolve with refund/no-refund/close |
| Reports | Listing reports table, dismiss action |
| Users | Searchable user table, toggle verified/active, delete |
| Listings | Searchable listings table, delete action |
| Activity Logs | Login history with IP addresses, action badges |

---

## 7. Authentication Flow

```
Registration:
  User fills form → POST /api/auth/register/
  → User created (is_verified=false)
  → Verification email sent with UUID token
  → User clicks link → GET /api/auth/verify-email/?token=xxx
  → is_verified=true → Can now login

Standard Login:
  POST /api/auth/login/ (username + password)
  → If email not verified → Error "verify your email"
  → If 2FA enabled → Error "2fa_required: true"
  → If valid → Returns { access, refresh } JWT tokens
  → Frontend stores in localStorage
  → Fetches user profile via GET /api/auth/me/

2FA Login:
  Standard login returns 2fa_required error
  → Frontend shows TOTP code input
  → POST /api/auth/login/2fa/ (username + password + code)
  → PyOTP verifies code against user's totp_secret
  → Returns { access, refresh } JWT tokens

Token Refresh:
  Access token expires (1 day) → 401 response
  → Axios interceptor catches it
  → POST /api/auth/token/refresh/ with refresh token
  → New access token stored
  → Original request retried
  → If refresh fails → Redirect to login

2FA Setup:
  POST /api/auth/2fa/setup/ → Returns QR code + secret
  → User scans QR in authenticator app
  → POST /api/auth/2fa/verify/ with 6-digit code
  → is_2fa_enabled=true

Password Reset:
  POST /api/auth/password-reset/ (email)
  → Email sent with reset token
  → POST /api/auth/password-reset/confirm/ (token + new password)
  → Password updated
```

---

## 8. Payment Flow

```
Buy Now / Accept Offer:
  1. POST /api/listings/<id>/buy/ (or accept offer)
     → Creates Order (status: pending_payment)
     → Listing marked as sold
     → Returns order_id

  2. Frontend redirects to /checkout/<order_id>

  3. POST /api/payments/create-intent/ { order_id }
     → Creates Stripe PaymentIntent (amount in cents, CAD)
     → Returns client_secret

  4. Frontend renders Stripe CardElement
     → User enters card details
     → stripe.confirmCardPayment(client_secret)

  5. Stripe sends webhook → POST /api/payments/webhook/
     → Event: payment_intent.succeeded
     → Payment status → 'succeeded'
     → Order status → 'paid'
     → Escrow status → 'held'
     → Receipt created
     → Notifications sent to buyer + seller
     → Emails sent to both parties

  6. If payment fails:
     → Payment status → 'failed'
     → Order status → 'cancelled'
     → Listing reopened (status → 'active')
```

---

## 9. Escrow & Buyer Protection

```
Payment Succeeds:
  → escrow_status = 'held' (funds held)

Seller Ships:
  → order.status = 'shipped'
  → Tracking number saved

Buyer Confirms Delivery:
  → order.status = 'delivered'
  → order.delivered_at = now
  → order.protection_expires_at = now + 7 days
  → Both parties notified

Protection Period (7 days):
  → Buyer can open a dispute
  → Escrow remains 'held'

If Dispute Opened:
  → escrow_status = 'disputed' (frozen)
  → Admin reviews and resolves:
    - Refund → escrow_status = 'refunded', Stripe refund issued
    - No refund → escrow_status = 'released'
    - Close → escrow_status = 'released'

If No Dispute After 7 Days:
  → Management command: python manage.py release_escrow
  → escrow_status = 'released'
  → Both parties notified

Escrow Status Flow:
  pending → held → released (normal)
  pending → held → disputed → refunded (dispute won by buyer)
  pending → held → disputed → released (dispute won by seller)
```

---

## 10. Safety & Security Features

### Rate Limiting
| Scope | Limit | Applied To |
|---|---|---|
| Anonymous | 60/minute | All unauthenticated requests |
| Authenticated | 120/minute | All authenticated requests |
| Auth (login/register) | 5/minute | Login, register, 2FA login |
| Listing Creation | 10/hour | Creating new listings |

### Content Moderation
- **Banned keywords**: counterfeit, replica, fake designer, knockoff, stolen, drugs, weapons, illegal
- **Suspicious pricing**: Listings priced below $1 CAD are auto-flagged
- **Auto-check**: Runs on listing create AND edit
- **Flagged listings**: Marked with `is_flagged=true` + reason

### Report Auto-Escalation
- Users can report listings for: fake, spam, inappropriate, sold, other
- Each user can only report a listing once
- At 3+ reports: listing is auto-hidden (status → 'closed'), seller notified
- Admin can view all reports and dismiss them

### User Blocking
- Any user can block another user
- Blocked users cannot: make offers, buy listings from the blocker
- Block check enforced at transaction points (buy_now, offer creation)

### Buyer Reputation
- Score computed from dispute history: excellent, good, fair, poor, new
- Based on ratio of disputes to total orders
- Available via API for sellers to check buyers

### Activity Logging
- Tracks: login, login_failed, register, password_reset, profile_update, 2fa_enabled, 2fa_disabled
- Records: IP address (from X-Forwarded-For), user agent, timestamp
- Viewable by admin in Support Panel

### Two-Factor Authentication
- TOTP-based (Google Authenticator, Authy compatible)
- QR code generated with `pyotp` + `qrcode` libraries
- 30-second window with ±1 valid window tolerance
- Requires current TOTP code to disable (prevents unauthorized removal)

---

## 11. Deployment Guide

### Backend (Render)

1. Create **Web Service** on Render
   - Repository: `github.com/jilspatel1412/SellIT`
   - Root Directory: `backend`
   - Runtime: Python 3
   - Build Command: `./build.sh`
   - Start Command: `gunicorn sellit.wsgi --log-file -`

2. Create **PostgreSQL** database on Render (free tier)

3. Set environment variables (see Section 12)

4. Deploy — `build.sh` runs:
   - `pip install -r requirements.txt`
   - `python manage.py collectstatic --noinput`
   - `python manage.py migrate`
   - `python manage.py create_admin`

### Frontend (Vercel)

1. Import project on Vercel
   - Repository: `github.com/jilspatel1412/SellIT`
   - Framework: Vite
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Output Directory: `dist`

2. Set environment variables:
   - `VITE_API_BASE_URL` = backend URL
   - `VITE_STRIPE_PUBLISHABLE_KEY` = Stripe pk_test key

3. Deploy

### Stripe Webhook

1. Stripe Dashboard → Webhooks → Add endpoint
2. URL: `https://<backend-url>/api/payments/webhook/`
3. Events: `payment_intent.succeeded`, `payment_intent.payment_failed`
4. Copy signing secret → set as `STRIPE_WEBHOOK_SECRET` on Render

### Management Commands

| Command | Purpose | When to Run |
|---|---|---|
| `python manage.py migrate` | Apply database migrations | Auto-runs on deploy |
| `python manage.py create_admin` | Create admin user from env vars | Auto-runs on deploy |
| `python manage.py seed_categories` | Seed 12 default categories | Auto-runs via migration |
| `python manage.py settle_auctions` | Close expired auctions, create orders | Cron job (every hour) |
| `python manage.py release_escrow` | Release funds after protection period | Cron job (daily) |

---

## 12. Environment Variables

### Backend (Render)

| Variable | Example | Required |
|---|---|---|
| `SECRET_KEY` | (random 50-char string) | Yes |
| `DEBUG` | `False` | Yes |
| `DATABASE_URL` | `postgresql://...` | Yes |
| `ALLOWED_HOSTS` | `sellit-ma71.onrender.com` | Yes |
| `FRONTEND_URL` | `https://sell-it-kohl.vercel.app` | Yes |
| `CORS_ALLOWED_ORIGINS` | `https://sell-it-kohl.vercel.app` | Yes |
| `STRIPE_SECRET_KEY` | `sk_test_...` | Yes |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` | Yes |
| `CLOUDINARY_CLOUD_NAME` | `your_cloud` | Yes |
| `CLOUDINARY_API_KEY` | `123456789` | Yes |
| `CLOUDINARY_API_SECRET` | `abc123...` | Yes |
| `BREVO_API_KEY` | `xkeysib-...` | Yes (for emails) |
| `DEFAULT_FROM_EMAIL` | `noreply@sellit.com` | Yes |
| `ADMIN_USERNAME` | `admin` | For auto-create |
| `ADMIN_EMAIL` | `admin@example.com` | For auto-create |
| `ADMIN_PASSWORD` | `securepass` | For auto-create |

### Frontend (Vercel)

| Variable | Example | Required |
|---|---|---|
| `VITE_API_BASE_URL` | `https://sellit-ma71.onrender.com` | Yes |
| `VITE_STRIPE_PUBLISHABLE_KEY` | `pk_test_...` | Yes |

---

## 13. Team Contributions

### Jils — Authentication, Security & Deployment
**Backend:** Users app (registration, login, email verification, password reset), 2FA (TOTP setup/verify/disable), activity logging, rate limiting, deployment config (settings.py, build.sh, Procfile, CORS)
**Frontend:** Login, Register, VerifyEmail, ResetPassword, Profile (2FA UI), AuthContext, Navbar

### Hetu — Listings, Search & Moderation
**Backend:** Listings app (CRUD, images, categories), search/filter system, offers (make/accept/reject), auctions (bids, settle command), content moderation, report system with auto-escalation, search alerts, seed_categories command
**Frontend:** Home, Listings, ListingDetail (share/report), CreateListing, EditListing, SellerListings, SellerOffers, BuyerFavorites, SearchAlerts, ListingCard, ImageGallery, BidForm, OfferForm, Countdown

### Utsav — Orders, Payments & Reviews
**Backend:** Orders app (order lifecycle), Stripe integration (PaymentIntent, webhooks), escrow system (hold/release/refund), release_escrow command, reviews with images, shipping label PDF generation, receipts
**Frontend:** BuyerOrders (escrow display, review modal, dispute modal), SellerOrders (escrow, ship modal), Checkout (Stripe Elements), OrderDetail (progress tracker, review form)

### Hitarth — Messaging, Notifications, Disputes & Admin
**Backend:** Messaging app (threads, send/receive, unread count), notifications app (in-app + Brevo emails), analytics app (revenue, search trends), disputes (open/resolve, escrow freeze), user blocking, buyer reputation scoring, admin endpoints
**Frontend:** Inbox (messaging UI), DisputeCenter, SupportPanel (5-tab admin panel), SellerDashboard (analytics charts), SellerProfile (block button, reviews)
