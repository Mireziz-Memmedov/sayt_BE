from .models import Listing, ListingImage, NewsUsers
from .serializers import NewsUsersSerializer, ListingSerializer, ListingImageSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
import secrets
import string
import resend
import threading
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

resend.api_key = settings.RESEND_API_KEY

def send_email_function(email, verify_code):
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": [email],
        "subject": "Verification Code",
        "html": f"<p>Your code: {verify_code}</p>"
    })

def send_email_async(email, verify_code):
    threading.Thread(
        target=send_email_function,
        args=(email, verify_code)
    ).start()

@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    
    NewsUsers.objects.filter(
        is_active = False,
        verify_code_created_at__lt=timezone.now() - timedelta(minutes=5)
    ).delete()

    if not username or not password or not email:
        return Response(
            {'success': False, 'error': 'All fields must be filled in!'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        validate_email(email)
    except ValidationError:
        return Response(
            {'success': False, 'error': 'The email format is incorrect!'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(password) < 8:
        return Response(
            {'success': False, 'error': 'Password must be at least 8 characters long.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if NewsUsers.objects.filter(username=username).exists():
        return Response(
            {'success': False, 'error': 'The username already exists!'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    if NewsUsers.objects.filter(email=email).exists():
        return Response(
            {'success': False, 'error': 'The email already exists!'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    verify_code = generate_verify_code(6)    

    user = NewsUsers(
        username = username,
        email = email,
        is_active = False,
        verify_code = verify_code,
        verify_code_created_at = timezone.now()
    )

    user.set_password(password)
    user.save()

    send_email_async(email, verify_code)
        
    return Response(
        {"success": True, "message": "Verification code sent successfully"},
        status=status.HTTP_200_OK
    )

def generate_verify_code(length):
    characters = string.digits
    password = ''.join(secrets.choice(characters) for i in range(length))

    return password

@api_view(['POST'])
@permission_classes([AllowAny])
def verify(request):
    verify_code = request.data.get('code')

    if not verify_code:
        return Response(
            {'success': False, 'error': 'Please enter the verification code.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user_instance = NewsUsers.objects.filter(verify_code=verify_code).first()

    if not user_instance:
        return Response(
            {'success': False, 'error': 'Invalid verification code.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if timezone.now() - user_instance.verify_code_created_at > timedelta(minutes=5):
        return Response(
            {'success': False, 'error': 'Your verification code has expired. Please request a new one.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user_instance.is_active = True
    user_instance.verify_code = None
    user_instance.save()

    return Response(
        {'success': True, 'message': 'Verification successful.'},
        status=status.HTTP_200_OK
    )
    
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username_or_email = request.data.get('username_or_email')
    password = request.data.get('password')

    if not username_or_email or not password:
        return Response(
            {'success': False, 'error': 'All fields must be filled in!'}, 
            status=status.HTTP_400_BAD_REQUEST
        ) 
    
    user = NewsUsers.objects.filter(
        Q(username=username_or_email) | Q(email=username_or_email)
    ).first()

    if not user:
        return Response(
            {'success': False, 'error': 'Invalid username/email or password.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not user.is_active:
        return Response(
            {'success': False, 'error': 'Please verify your account before logging in.'}, 
            status=status.HTTP_400_BAD_REQUEST
        ) 
        
    if not user.check_password(password):
       return Response(
            {'success': False, 'error': 'Invalid username/email or password.'}, 
            status=status.HTTP_400_BAD_REQUEST
        ) 

    print("USER:", user)
    print("USER ID:", user.id)

    refresh = RefreshToken.for_user(user)
    
    return Response(
        {
            'success': True,
            'message': 'Login successful.',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'username': user.username,
            'email': user.email,
        },
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
def add_listing(request):
    user = request.user
    
    make = request.data.get('make')
    model = request.data.get('model')
    year = request.data.get('year')
    body_type = request.data.get('body_type')
    fuel = request.data.get('fuel')
    transmission = request.data.get('transmission')
    engine = request.data.get('engine')
    mileage = request.data.get('mileage')
    color = request.data.get('color')
    price = request.data.get('price')
    description = request.data.get('description')
    images = request.FILES.getlist('images')

    if not make or not model:
        return Response({"success": False, "error": "Missing fields"})

    if not images:
        return Response({"error": "No images uploaded"})

    listing = Listing.objects.create(
        user=user,
        make=make,
        model=model,
        year=year,
        body_type=body_type,
        fuel=fuel,
        transmission=transmission,
        engine=engine,
        mileage=mileage,
        color=color,
        price=price,
        description=description
    )

    for img in images:
        ListingImage.objects.create(
            listing=listing,
            image=img
        )

    return Response({
        "success": True,
        "message": "Listing created successfully"
    }, status=status.HTTP_201_CREATED)



