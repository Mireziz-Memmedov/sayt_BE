from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from cloudinary.models import CloudinaryField

class NewsUsers(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128, null=False)
    email = models.EmailField(max_length=254, unique=True, null=False, blank=False)
    verify_code = models.CharField(max_length=6, null=True, blank=True)
    verify_code_created_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'sayt'

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

class Listing(models.Model):
    user = models.ForeignKey(NewsUsers, on_delete=models.CASCADE, related_name='listings')

    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    body_type = models.CharField(max_length=50)
    fuel = models.CharField(max_length=50)
    transmission = models.CharField(max_length=50)
    engine = models.CharField(max_length=50)
    mileage = models.IntegerField()
    color = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return f"{self.make} {self.model} ({self.year}) - {self.user.username}"

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')

    image = CloudinaryField('image', null=True, blank=True)

    def __str__(self):
        return f"{self.listing.make} {self.listing.model} image"
