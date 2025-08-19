from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from decouple import config

class GoogleIDTokenLogin(APIView):
    def post(self, request):
        token = request.data.get("access_token")
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), config('GOOGLE_CLIENT_ID'))
            # idinfo has 'email', 'sub', 'name', etc.
            email = idinfo['email']
            user, created = User.objects.get_or_create(email=email, defaults={'username': email.split('@')[0], 'first_name': idinfo.get('given_name', '')})

            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "email": user.email
                }
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            print("Google token verification error:", e)
            return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)
