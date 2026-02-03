import uuid
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

class Resume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    
    # File Storage
    file = models.FileField(upload_to='resumes/%Y/%m/%d/', # upload_to='resumes/%Y/%m/%d/' will organize them by date (e.g., resumes/2026/01/30/my_resume.pdf). This prevents "filename collisions"
                            validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # AI Data
    raw_text = models.TextField(blank=True, null=True) # extracted raw text from resume, this will go to the AI model
    structured_data = models.JSONField(blank=True, null=True) # AI model will return json structure with reume details
    
    def __str__(self):
        return f"Resume - {self.user.username} ({self.uploaded_at})"