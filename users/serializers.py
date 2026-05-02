from rest_framework import serializers
from .models import NewUsers

class NewsUsersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = NewUsers
        fields = ['id', 'username', 'password', 'email']