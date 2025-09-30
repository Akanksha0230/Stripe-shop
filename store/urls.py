from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("",views.index, name="index"),
    path("create-checkout-session/",views.create_checkout_session, name="create_checkout_session"),
    path("success/", views.success, name="success"),
]