# Stripe Checkout Demo — Django app

## Summary / Assumptions
- Single-page store showing **3 fixed products** (created automatically if missing).
- User enters quantities and clicks **Buy**. The app uses **Stripe Checkout (test mode)** to process the payment.
- After successful payment user is redirected back; server confirms payment and marks the `Order` as paid. Paid orders are shown in the “My Orders” area on the main page.
- No user authentication (optional).

## Flow chosen
- **Stripe Checkout** is used. Rationale: easiest secure flow for collecting card details and handling SCA. The server creates a Checkout Session and redirects the user to Stripe. On success, Stripe redirects back with `session_id`; server verifies `payment_status` by retrieving the session and marks the corresponding DB order `paid=True`. (No sensitive card data in our server.)

## How double-charge / inconsistent state is avoided
1. **Stripe Checkout** ensures a Checkout Session is charged only once.
2. We create an `Order` **server-side before** redirecting to Stripe and store `stripe_session_id` (unique constraint). This gives an idempotent server-side record tied to the checkout session.
3. On return (`/success/?session_id=...`) we call `stripe.checkout.Session.retrieve(session_id)` and only set `paid=True` if Stripe reports the session paid. If the user refreshes the success page, the `Order` already exists and will not be double-created due to the unique constraint.
4. Button is disabled on submit to reduce the chance of double-submit from the client.

> For higher robustness in production, add a Stripe webhook endpoint to mark orders paid server-side on `checkout.session.completed`, and validate webhook signatures. For local dev you can use the Stripe CLI to forward events.

## Setup / Run
1. Create a Python virtualenv and install requirements:
   ```bash
   python -m venv venv
   venv/Scripts/activate
   pip install -r requirements.txt
