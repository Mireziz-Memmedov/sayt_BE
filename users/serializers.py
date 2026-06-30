from rest_framework import serializers
from .models import Listing, ListingImage, NewsUsers
from datetime import timedelta
from django.utils import timezone

class ListingImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = ListingImage
        fields = ['id', 'image']
    
    def get_image(self, obj):
        # CloudinaryField'dən tam URL'ni al
        if obj.image:
            return obj.image.url
        return None

class ListingSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)
    time = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = ['id', 'user', 'make', 'model', 'year', 'body_type', 'fuel', 'transmission', 'engine', 'mileage', 'color', 'price', 'description', 'images', 'time']

    def get_time(self, listing):
        today = timezone.now().date()
        listing_date = listing.time.date()

        if listing_date == today:
            return "Today" + " " + listing.time.strftime("%H:%M")

        elif listing_date == today - timedelta(days=1):
            return "Yesterday" + " " + listing.time.strftime("%H:%M")

        else:
            return listing.time.strftime("%d.%m.%Y, %H:%M")        

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



