from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from PIL import Image
import base64, os, io
from django.conf import settings
# Create your views here.

class UserLogin(APIView):
    
    permission_classes = [AllowAny]

    def post(self, request):
        # Logic for user login
        print(request.data)
        data = request.data.copy()
        username = data["username"]
        password = data["password"]

        response_data = {}

        # Check user existence
        if not User.objects.filter(username=username).exists():
            response_data["message"] = "User not found"
            return Response(response_data, status=status.HTTP_404_NOT_FOUND, content_type="application/json")

        # Authenticate user
        user = authenticate(username=username, password=password)
        print("user ", user)

        if not user:
            response_data["message"] = "Username or Password is wrong"
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED, content_type="application/json")
        
        serializer = UserSerializer(user)

        refresh_token = RefreshToken.for_user(user)

        response_data["message"] = "Login Success"
        response_data["data"] = serializer.data
        response_data["access_token"] = str(refresh_token.access_token)
        response_data["refresh_token"] = str(refresh_token)

        return Response(response_data, status=status.HTTP_200_OK, content_type="application/json")
    

class UserSignup(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.copy()
        username = data["username"]
        password = data["password"]

        response_data = {}

        # Check user existence
        if User.objects.filter(username=username).exists():
            response_data["message"] = "Username already exists"
            return Response(response_data, status=status.HTTP_403_FORBIDDEN, content_type="application/json")
        
        with transaction.atomic():

            # Register user
            user = User(username=username)
            user.set_password(password)
            user.save()
            
            userProfile.objects.create(user=user)

        # login user
        login(request, user)

        # # Authenticate user
        # user = authenticate(request, username=user.username, password=user.password)
        # print("user ", user)
        # if not user:
        #     response_data["message"] = "Authentication failed"
        #     return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type="application/json")

        refresh_token = RefreshToken.for_user(user)
        

        serializer = UserSerializer(user)


        response_data["message"] = "User Signup Success"
        response_data["data"] = serializer.data
        response_data["access_token"] = str(refresh_token.access_token)
        response_data["refresh_token"] = str(refresh_token)

        return Response(response_data, status=status.HTTP_200_OK, content_type="application/json")


class UserProfileManagement(APIView):
    def put(self, request):

        # Get request body
        data = request.data.copy()
        response_data = {}

        if "user_id" not in data:
            response_data["message"] = "user_id is required"
            return Response(response_data, status=status.HTTP_422_UNPROCESSABLE_ENTITY, content_type="application/json")
        
        try:
            user_id = int(data["user_id"])
        except TypeError:
            response_data["message"] = f"Invalid valid user_id {user_id}"
            return Response(response_data, status=status.HTTP_422_UNPROCESSABLE_ENTITY, content_type="application/json")

        user = User.objects.filter(id=user_id)

        if not user.exists():
            response_data["message"] = "User not found"
            return Response(response_data, status=status.HTTP_404_NOT_FOUND, content_type="application/json")
        
        user = user.first()

        if "profile_picture" in data:
            image_bytes = base64.b64decode(data["profile_picture"])
            image_buffer = io.BytesIO(image_bytes)
            image = Image.open(image_buffer)

            image_path = os.path.join(settings.__getattr__("MEDIA_ROOT"), "user", f"{user_id}-profile-picture.png")
            image.save(image_path)

            relative_path = os.path.relpath(image_path, settings.__getattr__("BASE_DIR"))
            user.user_profile.profile_picture = relative_path
        
        user.user_profile.bio = data["bio"]
        user.user_profile.location = data["location"]
        user.user_profile.date_of_birth = data["date_of_birth"]
        user.user_profile.save()

        serializer = UserSerializer(user)
        response_data["message"] = "User Profile Update Success"
        response_data["data"] = serializer.data

        return Response(response_data, status=status.HTTP_200_OK, content_type="application/json")
        

        

