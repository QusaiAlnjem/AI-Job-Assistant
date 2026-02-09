from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobMatchViewSet, SearchJobsView, CheckJobView

router = DefaultRouter()
router.register(r'matches', JobMatchViewSet, basename='jobmatch')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', SearchJobsView.as_view(), name='job-search'),
    path('check/', CheckJobView.as_view(), name='job-check'),
]