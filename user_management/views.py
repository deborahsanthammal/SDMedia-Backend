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
import json
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


