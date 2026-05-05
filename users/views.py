from .models import NewsUsers
from .serializers import NewsUsersSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import secrets
import string

@api_view(["POST"])
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

    send_mail(
        subject = 'Email Verification Code',
        message=f'Your verification code is: {verify_code}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    return Response(
        {'success': True, 'message': 'Verification code sent successfully'}, 
        status=status.HTTP_201_CREATED
    )

def generate_verify_code(length):
    characters = string.digits
    password = ''.join(secrets.choice(characters) for i in range(length))

    return password