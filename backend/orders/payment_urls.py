from django.urls import path
from . import views

urlpatterns = [
    path('create-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('confirm/', views.confirm_payment, name='confirm_payment'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]
