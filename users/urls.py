from django.urls import path
from .views import RegisterAPIView, change_password, reset_password, ProfileViewSet

from rest_framework.routers import DefaultRouter
router = DefaultRouter()


router.register(r'profile-update', ProfileViewSet)

urlpatterns = [
    path('register/', RegisterAPIView.as_view()),
    path('change-password/', change_password),
    path('reset-password/', reset_password),
]

urlpatterns += router.urls