from rest_framework import serializers
from .models import User, Seller, Product, Review, Issue, Payment, DeliveryHub, Platform

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    seller = SellerSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    seller = SellerSerializer(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'

class IssueSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    seller = SellerSerializer(read_only=True)

    class Meta:
        model = Issue
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    seller = SellerSerializer(read_only=True)
    delivery = serializers.StringRelatedField()  # Shows hub_name

    class Meta:
        model = Payment
        fields = '__all__'

class DeliveryHubSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryHub
        fields = '__all__'

class PlatformSerializer(serializers.ModelSerializer):
    seller = SellerSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Platform
        fields = '__all__'
