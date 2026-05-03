from .models import NewsUsers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import status

@api_view(["POST"])
def signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

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

    user = NewsUsers.objects.create(
        username = username,
        email = email
    )

    user.set_password(password)
    user.save()

    return Response(
        {'success': True, 'message': 'Account created successfully'}, 
        status=status.HTTP_201_CREATED
    )