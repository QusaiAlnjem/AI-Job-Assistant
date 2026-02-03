from django.shortcuts import render
from rest_framework import viewsets, parsers
from rest_framework.permissions import IsAuthenticated
from .models import Resume
from .serializers import ResumeSerializer
from .services import extract_text_from_file, parse_resume_with_ai

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
        instance = serializer.save(user=self.request.user)
        filepath = instance.file.path
        raw_text = extract_text_from_file(filepath)
        if raw_text:
            instance.raw_text = raw_text
            ai_data = parse_resume_with_ai(raw_text)
            
            if ai_data:
                instance.structured_data = ai_data
                
            instance.save()


