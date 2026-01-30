from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Extends the default Django User.
    We add fields relevant to a job seeker.
    Default Django User Attributes:
        username, password, email, first_name, last_name
        is_active, is_staff, is_superuser
    """
    bio = models.TextField(blank=True, null=True, help_text="Short professional bio")
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.username