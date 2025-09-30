from django.shortcuts import render, redirect
import os
from django.conf import settings
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.db import transaction, IntegrityError
from .models import Product, Order, OrderItem
import stripe
# Create your views here.
stripe.api_key= settings.STRIPE_SECRET_KEY

def index(request):
    products_data = [
        {"sku": "p1","name":"Red T-shirt","price_cents": 1999},
        {"sku": "p2","name":"Blue Mug","price_cents": 1299},
        {"sku": "p3","name":"Sticker Pack","price_cents": 499},
    ]
    for pd in products_data:
        Product.objects.get_or_create(sku=pd["sku"],defaults={"name":pd["name"],"price_cents":pd["price_cents"]})

    products = Product.objects.all().order_by("sku")
    orders = Order.objects.filter(paid=True).order_by("-created_at")
    return render(request,"store/index.html",{
             "products": products,
             "orders": orders,
             "stripe_pub_key": settings.STRIPE_PUBLISHABLE_KEY,
    })


@require_POST
def create_checkout_session(request):
    """
    Expects POST with quantities: quantity_<product.pk> keys (integers).
    Creates Stripe Checkout Session and an Order record with stripe_session_id.
    Redirects client to session.url
    """
    quantities = {}
    for k,v in request.POST.items():
        if k.startswith("quantity_"):
            try:
                pid = int(k.split("_",1)[1])
                qty = int(v)
                if qty > 0:
                    quantities[pid] = qty
            except Exception:
                continue
    if not quantities:
        return HttpResponseBadRequest("No quantities provided")
    
    line_items = []
    total = 0
    for pid, qty in quantities.items():
        try:
            p = Product.objects.get(pk=pid)
        except Product.DoesNotExist:
            return HttpResponseBadRequest("Invaild Product")
            
        line_items.append({
            "price_data": {
                "currency": "usd",
                "unit_amount": p.price_cents,
                "product_data": {"name": p.name},
            },
            "quantity": qty,
        })
        total += p.price_cents * qty

    success_url = request.build_absolute_uri("/store/success/") + "?session_id={CHECKOUT_SESSION_ID}"
    cancle_url = request.build_absolute_uri("/store/")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=line_items,
            success_url=success_url,
            cancel_url=cancle_url,
        )
    except Exception as e:
        return HttpResponseBadRequest(f"Stripe error:{str(e)}")


    try:
        with transaction.atomic():
            order= Order.objects.create(stripe_session_id=session["id"], total_cents=total, paid=False)
            for pid, qty in quantities.items():
                p = Product.objects.get(pk=pid)
                OrderItem.objects.create(order=order, product= p, quantity=qty, unit_price_cents=p.price_cents)
    except IntegrityError:
        pass
    

    return JsonResponse({"url":session.url})

def success(request):
    """
    After Stripe Checkout, user is redirected here with session_id. We confirm payment
    status via Stripe API, update Order.paid accordingly and then show the main page.
    """
    session_id = request.GET.get("session_id")
    if not session_id:
        return redirect("store:index")

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        return redirect("store:index")
    
    paid = session.get("payment_status") == "paid"

    #Mark order paid if not already
    try:
        order = Order.objects.get(stripe_session_id=session_id)
        if paid and not order.paid:
            order.paid = True
            order.save()
    except Order.DoesNotExist:
        # If an order wasn't created server-side (unlikely), create one from session info
        # For robustness, create a minimal record (not parsing items)
        Order.objects.create(stripe_session_id=session_id,paid=paid, total_cents=0)
    
    # show success page then provide link back to main page which will list paid orders
    return render(request, "store/success.html", {"paid":paid})