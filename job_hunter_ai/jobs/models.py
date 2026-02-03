from django.db import models
from django.conf import settings
from resumes.models import Resume

class Job(models.Model):
    """
    Represents a raw job posting scraped from the web.
    """
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField() # Full job text
    url = models.URLField(unique=True) # Prevent duplicates
    source = models.CharField(max_length=50, default="Web") # e.g., "Indeed", "LinkedIn"
    posted_at = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company}"

class JobMatch(models.Model):
    """
    Stores the AI analysis of how well a specific Resume fits a specific Job.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True)
    match_score = models.IntegerField(default=0) # AI scoring from 0 to 100
    ai_analysis = models.JSONField(default=dict) # Structured advice from AI
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job') # A user can't have two matches for the same job

    def __str__(self):
        return f"{self.user.username} - {self.job.title} ({self.match_score}%)"