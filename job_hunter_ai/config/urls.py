from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # API Endpoints
    path('api/users/', include('users.urls')), # Connects new users URLs
    path('api/', include('resumes.urls')), # Connects new resumes URLs
    path('api/', include('jobs.urls')), # Connects new jobs URLs
]

# This allows serving uploaded files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)