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
    return HttpResponse("""
        <h1>Welcome to the Ecommerce API</h1>
        <h3>Select a Table</h3>

        <select onchange="if(this.value) window.location.href=this.value;">
            <option value="">-- Select Table --</option>
            <option value="/api/users/">Users</option>
            <option value="/api/sellers/">Sellers</option>
            <option value="/api/products/">Products</option>
            <option value="/api/reviews/">Reviews</option>
            <option value="/api/issues/">Issues</option>
            <option value="/api/payments/">Payments</option>
            <option value="/api/deliveryhubs/">Delivery Hubs</option>
            <option value="/api/platforms/">Platforms</option>
        </select>
    """)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class SellerViewSet(viewsets.ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class DeliveryHubViewSet(viewsets.ModelViewSet):
    queryset = DeliveryHub.objects.all()
    serializer_class = DeliveryHubSerializer

class PlatformViewSet(viewsets.ModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer


from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def api_home(request):
    return Response({
        "Select Table": {
            "Users": "/api/users/",
            "Sellers": "/api/sellers/",
            "Products": "/api/products/",
            "Reviews": "/api/reviews/",
            "Issues": "/api/issues/",
            "Payments": "/api/payments/",
            "Delivery Hubs": "/api/deliveryhubs/",
            "Platforms": "/api/platforms/",
        }
    })



