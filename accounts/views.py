from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from accounts.serializers import *
from drf_spectacular.utils import extend_schema, OpenApiParameter



@extend_schema(request=RegisterSerializer, responses={201: UserSerializer})
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data = request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)


@extend_schema(request=LoginSerializer, responses={200: UserSerializer})
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    password = serializer.validated_data.get('password')

    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh":str(refresh),
            "access":str(refresh.access_token),
            "user":{
                "id":user.id,
                "username":user.username
            }
            }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    
@extend_schema(request=TokenRefreshSerializer, responses={200: TokenRefreshSerializer})
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    serializer = TokenRefreshSerializer(data = request.data)
    try:
        serializer.is_valid(raise_exception=True)
    except Exception as err:
        return Response({"error": str(err)}, status=400)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(request=LogoutSerializer, responses={200: None})
@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    token = request.data.get("refresh")
    refresh = RefreshToken(token=token)
    refresh.blacklist()
    return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)

@extend_schema(responses=UserSerializer)
@api_view(['GET'])
def profile_view(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)