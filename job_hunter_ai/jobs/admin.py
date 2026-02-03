from django.contrib import admin
from .models import Job, JobMatch

class JobMatchAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'match_score', 'created_at')
    list_filter = ('match_score',)

admin.site.register(Job)
admin.site.register(JobMatch, JobMatchAdmin)