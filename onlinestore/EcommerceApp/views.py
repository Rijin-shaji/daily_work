from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from rest_framework import viewsets
from .models import User, Seller, Product, Review, Issue, Payment, DeliveryHub, Platform
from .serializers import (
    UserSerializer, SellerSerializer, ProductSerializer,
    ReviewSerializer, IssueSerializer, PaymentSerializer,
    DeliveryHubSerializer, PlatformSerializer
)

def home(request):
    return HttpResponse("Welcome to the Ecommerce API!")
# ----------------------
# User ViewSet
# ----------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# ----------------------
# Seller ViewSet
# ----------------------
class SellerViewSet(viewsets.ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer

# ----------------------
# Product ViewSet
# ----------------------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# ----------------------
# Review ViewSet
# ----------------------
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

# ----------------------
# Issue ViewSet
# ----------------------
class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

# ----------------------
# Payment ViewSet
# ----------------------
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

# ----------------------
# DeliveryHub ViewSet
# ----------------------
class DeliveryHubViewSet(viewsets.ModelViewSet):
    queryset = DeliveryHub.objects.all()
    serializer_class = DeliveryHubSerializer

# ----------------------
# Platform ViewSet
# ----------------------
class PlatformViewSet(viewsets.ModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer

