from django.shortcuts import render
from rest_framework import viewsets, parsers
from rest_framework.permissions import IsAuthenticated
from .models import Resume
from .serializers import ResumeSerializer

class ResumeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows resumes to be viewed or edited.
    """
    serializer_class = ResumeSerializer
    permission_classes = [IsAuthenticated] # Only logged-in users can upload
    parser_classes = [parsers.MultiPartParser, parsers.FormParser] # Tells Django to expect a file upload, not text

    def get_queryset(self):
        # Ensure users can only see their OWN resumes, not everyone else's
        return Resume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the uploader as the owner of the resume
        serializer.save(user=self.request.user)
        
        # NOTE: This is where we will trigger the AI parsing later!
        # e.g., process_resume_task.delay(resume.id)