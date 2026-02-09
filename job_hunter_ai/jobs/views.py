from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import JobMatch, Job
from .serializers import JobMatchSerializer
from .services import search_and_save_jobs, analyze_job_match
from resumes.models import Resume
import uuid

class JobMatchViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = JobMatchSerializer

    http_method_names = ['get', 'patch', 'head', 'options']

    def get_queryset(self):
        # Only show matches for the logged-in user, ordered by highest score
        print(self.request.user)
        return JobMatch.objects.filter(user=self.request.user).order_by('-match_score')

class SearchJobsView(APIView):
    """
    POST /api/jobs/search/
    Body: { "query": "Python Developer" }
    
    1. Scrapes WWR for the query.
    2. Matches results against user's latest resume.
    3. Returns the analyzed matches.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def post(self, request):
        title = request.data.get('title')
        job_type = request.data.get('job_type') 
        location = request.data.get('location')

        if not title:
            return Response({"error": "Job Title is required"}, status=status.HTTP_400_BAD_REQUEST)

        resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()
        if not resume:
            return Response({"error": "Please upload a resume first!"}, status=status.HTTP_400_BAD_REQUEST)

        print(f"User {request.user.username} searching: {title} | Loc: {location} | Type: {job_type}")

        # Call Service with separated args
        jobs = search_and_save_jobs(title, location, job_type)
        
        if not jobs:
            return Response({"message": "No new jobs found."}, status=status.HTTP_200_OK)

        # AI Matching
        matches = []
        for job in jobs:
            match = analyze_job_match(request.user, resume, job)
            if match:
                matches.append(match)

        serializer = JobMatchSerializer(matches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CheckJobView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        title = request.data.get('title', 'Unknown Role')
        description = request.data.get('description')

        if not description:
            return Response({"error": "Job description is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Get Resume
        resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()
        if not resume:
            return Response({"error": "Please upload a resume first!"}, status=status.HTTP_400_BAD_REQUEST)

        # Create Job with UNIQUE URL
        unique_id = str(uuid.uuid4())
        
        job = Job.objects.create(
            title=title,
            company="Manual Entry",
            description=description,
            url=f"https://manual-check.com/{request.user.id}/{unique_id}", 
            source="Manual Check"
        )

        match = analyze_job_match(request.user, resume, job)
        
        if match:
            serializer = JobMatchSerializer(match)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Could not analyze job."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)