from rest_framework import serializers
from .models import User, Seller, Product, Review, Issue, Payment, DeliveryHub, Platform

# ----------------------
# User Serializer
# ----------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


# ----------------------
# Seller Serializer
# ----------------------
class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'


# ----------------------
# Product Serializer
# ----------------------
class ProductSerializer(serializers.ModelSerializer):
    # Nested relationships (optional)
    seller = SellerSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


# ----------------------
# Review Serializer
# ----------------------
class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    seller = SellerSerializer(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'


# ----------------------
# Issue Serializer
# ----------------------
class IssueSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    seller = SellerSerializer(read_only=True)

    class Meta:
        model = Issue
        fields = '__all__'


# ----------------------
# Payment Serializer
# ----------------------
class PaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    seller = SellerSerializer(read_only=True)
    delivery = serializers.StringRelatedField()  # Shows hub_name

    class Meta:
        model = Payment
        fields = '__all__'


# ----------------------
# DeliveryHub Serializer
# ----------------------
class DeliveryHubSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryHub
        fields = '__all__'


# ----------------------
# Platform Serializer
# ----------------------
class PlatformSerializer(serializers.ModelSerializer):
    seller = SellerSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Platform
        fields = '__all__'
