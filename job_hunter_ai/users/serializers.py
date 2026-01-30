from djangorestframework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # Fields the frontend is allowed to see/edit
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'bio', 'linkedin_url']
        read_only_fields = ['id']