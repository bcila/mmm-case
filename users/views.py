from django.shortcuts import render
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import EmailTokenObtainPairSerializer
from drf_spectacular.utils import extend_schema

@extend_schema(
    request=RegisterSerializer,
    responses={201: RegisterSerializer},
    description="User registration endpoint."
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

@extend_schema(
    request=EmailTokenObtainPairSerializer,
    responses={200: EmailTokenObtainPairSerializer},
    description="Obtain JWT token by email and password."
)
class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
