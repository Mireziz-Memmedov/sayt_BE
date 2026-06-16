from rest_framework import serializers
from .models import Listing, ListingImage, NewsUsers

class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'image']

class ListingSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'user', 'make', 'model', 'year', 'body_type', 'fuel', 'transmission', 'engine', 'mileage', 'color', 'price', 'description', 'images']

class NewsUsersSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = NewsUsers
        fields = ['id', 'username', 'password', 'email']
    
    def create(self, validated_data):
        user = NewsUsers(
            username=validated_data['username'],
            email=validated_data['email']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user



