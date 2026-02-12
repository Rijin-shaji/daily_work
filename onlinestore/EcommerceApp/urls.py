from django.urls import path, include
from rest_framework import routers
from .views import (
    UserViewSet, SellerViewSet, ProductViewSet,
    ReviewViewSet, IssueViewSet, PaymentViewSet,
    DeliveryHubViewSet, PlatformViewSet,home
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'sellers', SellerViewSet)
router.register(r'products', ProductViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'issues', IssueViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'deliveryhubs', DeliveryHubViewSet)
router.register(r'platforms', PlatformViewSet)

# Include router URLs
urlpatterns = [
    path('', home),
    path('', include(router.urls)),
]
