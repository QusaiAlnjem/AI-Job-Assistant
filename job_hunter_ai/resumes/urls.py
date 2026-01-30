from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResumeViewSet

# The Router automatically creates URLs like /resumes/ and /resumes/{id}/
router = DefaultRouter()
router.register(r'resumes', ResumeViewSet, basename='resume')

urlpatterns = [
    path('', include(router.urls)),
]