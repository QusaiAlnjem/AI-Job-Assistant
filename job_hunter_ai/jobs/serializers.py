from rest_framework import serializers
from .models import Job, JobMatch

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

class JobMatchSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)

    class Meta:
        model = JobMatch
        fields = ['id', 'job', 'match_score', 'ai_analysis', 'created_at']