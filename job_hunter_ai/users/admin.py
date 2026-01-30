from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Using the default UserAdmin logic but for CustomUser
class CustomUserAdmin(UserAdmin):
    # Adding new fields to the "fieldsets" so they appear in the admin UI
    fieldsets = UserAdmin.fieldsets + (
        ('Professional Info', {'fields': ('bio', 'linkedin_url', 'github_url', 'portfolio_url')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)