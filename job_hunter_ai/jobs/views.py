from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import JobMatch
from .serializers import JobMatchSerializer
from .services import search_and_save_jobs, analyze_job_match
from resumes.models import Resume

class JobMatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoint: The user sees their matches here.
    (Matches are created by the background scraper, not by the user manually)
    """
    serializer_class = JobMatchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show matches for the logged-in user, ordered by highest score
        return JobMatch.objects.filter(user=self.request.user).order_by('-match_score')

class SearchJobsView(APIView):
    """
    POST /api/jobs/search/
    Body: { "query": "Python Developer" }
    
    1. Scrapes WWR for the query.
    2. Matches results against user's latest resume.
    3. Returns the analyzed matches.
    """
    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response({"error": "Query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        # We assume the user has at least one resume. We take the latest.
        resume = Resume.objects.filter(user=request.user).order_by('-uploaded_at').first()
        
        if not resume:
            return Response({"error": "Please upload a resume first!"}, status=status.HTTP_400_BAD_REQUEST)

        # Runing the Scraper
        print(f"🔍 User {request.user.username} is searching for: {query}")
        jobs = search_and_save_jobs(query)
        
        if not jobs:
            return Response({"message": "No new jobs found."}, status=status.HTTP_200_OK)

        # Runing AI Matching
        matches = []
        for job in jobs:
            match = analyze_job_match(request.user, resume, job)
            if match:
                matches.append(match)

        # Serialize and Return
        serializer = JobMatchSerializer(matches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

