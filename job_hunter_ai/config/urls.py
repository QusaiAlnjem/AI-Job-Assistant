from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- API Endpoints ---
    path('api/users/', include('users.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/', include('resumes.urls')),

    # --- Frontend Pages ---
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('index.html', TemplateView.as_view(template_name='index.html')),
    path('login.html', TemplateView.as_view(template_name='login.html')),
    path('signup.html', TemplateView.as_view(template_name='signup.html')),
    path('dashboard.html', TemplateView.as_view(template_name='dashboard.html')),
    path('profile.html', TemplateView.as_view(template_name='profile.html')),
    path('scanner.html', TemplateView.as_view(template_name='scanner.html')),
    path('results.html', TemplateView.as_view(template_name='results.html')),
    path('job_check.html', TemplateView.as_view(template_name='job_check.html'))
]

# This allows Django to serve uploaded files (Resumes) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
