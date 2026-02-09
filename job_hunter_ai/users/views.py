from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth import get_user_model, authenticate
from .serializers import RegisterSerializer, UserSerializer
import requests
from django.conf import settings

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny] # Anyone can sign up
    serializer_class = RegisterSerializer
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        recaptcha_token = request.data.get('captchaToken')
        if not recaptcha_token:
            return Response(
                {'error': 'CAPTCHA verification is required.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:    
            google_response = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data={
                    'secret': settings.RECAPTCHA_SECRET_KEY,
                    'response': recaptcha_token
                }
            )
            result = google_response.json()

            if not result.get('success'):
                return Response(
                    {'error': 'Invalid CAPTCHA. Please try again.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            print(f"CAPTCHA Error: {e}")
            return Response(
                {'error': 'Error verifying CAPTCHA. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 1. Save the User
        user = serializer.save()

        # 2. Create (or get) the Token for this user
        token, created = Token.objects.get_or_create(user=user)

        # 3. Create a custom response with the token
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "success": True,
                "user_id": user.pk,
                "username": user.username,
                "email": user.email,
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    # Security Parameter: 5 attempts per minute
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        # Authenticate checks the DB for this user/pass combo
        user = authenticate(username=username, password=password)
        
        if user:
            # Generate or Retrieve the Token
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                "token": token.key,      # Frontend needs this!
                "user_id": user.pk,
                "username": user.username
            })
        else:
            return Response(
                {"error": "Invalid Credentials"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        # Ensure the user can only see/edit their OWN profile
        return self.request.user