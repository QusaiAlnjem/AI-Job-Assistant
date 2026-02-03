from django.contrib import admin
from .models import Resume

class ResumeAdmin(admin.ModelAdmin):
    # What columns to show in the list view
    list_display = ('user', 'uploaded_at', 'id')
    
    # Add filters on the right side
    list_filter = ('uploaded_at',)
    
    # Make the JSON data read-only so you don't accidentally break it
    readonly_fields = ('uploaded_at', 'raw_text', 'structured_data')

# Register the model with our custom configuration
admin.site.register(Resume, ResumeAdmin)