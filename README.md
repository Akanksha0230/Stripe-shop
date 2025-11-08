# Stripe Checkout Demo — Django app

## Summary / Assumptions
- Single-page store showing **3 fixed products** (created automatically if missing).
- User enters quantities and clicks **Buy**. The app uses **Stripe Checkout (test mode)** to process the payment.
- After successful payment user is redirected back; server confirms payment and marks the `Order` as paid. Paid orders are shown in the “My Orders” area on the main page.
- Database used: PostgreSQL.
- Orders + items stored server-side to avoid losing state if client refreshes.

## Flow Chosen
- **Stripe Checkout Session** instead of Payment Intents.
  - Easier integration for test project.
  - Automatically handles redirects, card input, and confirmation.
  - Less boilerplate than Payment Intents.

## Avoiding Double Charge / Inconsistent State
- Each `Order` is tied to a unique `stripe_session_id`.
- Used `transaction.atomic()` to ensure order + items creation is consistent.
- `get_or_create` used for products to avoid duplicates.
- Success view rechecks Stripe API status before marking order `paid`.

## Setup / Run
1. Database setup:
   ```bash
      psql -U postgres
      CREATE DATABASE stripe_shop_db; 

2. Build Django Project and models:
   ```bash
      django-admin startproject stripe_shop .
      python manage.py startapp store 

3. Create a Python virtualenv and install requirements:
   ```bash
   python -m venv venv
   venv/Scripts/activate
   pip install -r requirements.txt
 
4. Migrate database:
   ```bash
      python manage.py makemigrations
      python manage.py migrate

5. Run Server:
   ```bash
      python manage.py runserver

Finally to test  payment Enter some product quantities → click Buy. Stripe Checkout page opens. Use test card Example: 4242 4242 4242 4242 Fill any future date and cvv any no. 
After success, you’ll be redirected back to /store/success/.
Return to main page → see your paid order in “My Orders”.
