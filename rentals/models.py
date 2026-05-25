from django.db import models
from django.contrib.auth.models import User
import uuid

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    FUEL_CHOICES = [
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('CNG', 'CNG'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid'),
    ]

    title = models.CharField(max_length=150)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='vehicles')
    overview = models.TextField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    fuel_type = models.CharField(max_length=50, choices=FUEL_CHOICES)
    model_year = models.IntegerField()
    seating_capacity = models.IntegerField()
    
    # Django allows upload_to relative to MEDIA_ROOT
    image1 = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    image2 = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    image3 = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    image4 = models.ImageField(upload_to='vehicles/', blank=True, null=True)

    # Accessories/Features
    air_conditioner = models.BooleanField(default=False)
    power_door_locks = models.BooleanField(default=False)
    anti_lock_braking = models.BooleanField(default=False)
    brake_assist = models.BooleanField(default=False)
    power_steering = models.BooleanField(default=False)
    driver_airbag = models.BooleanField(default=False)
    passenger_airbag = models.BooleanField(default=False)
    power_windows = models.BooleanField(default=False)
    cd_player = models.BooleanField(default=False)
    central_locking = models.BooleanField(default=False)
    crash_sensor = models.BooleanField(default=False)
    leather_seats = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand.name} {self.title} ({self.model_year})"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Cancelled', 'Cancelled'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bookings')
    booking_number = models.CharField(max_length=20, unique=True, editable=False)
    from_date = models.DateField()
    to_date = models.DateField()
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.booking_number:
            # Generate a clean numeric booking number
            self.booking_number = "BK" + uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.booking_number} - {self.vehicle} by {self.user.username}"

class Testimonial(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonials')
    testimonial_text = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Inactive')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial by {self.user.username} ({self.status})"

class ContactQuery(models.Model):
    STATUS_CHOICES = [
        ('Read', 'Read'),
        ('Unread', 'Unread'),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unread')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query from {self.name} - {self.email} ({self.status})"

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class ContactInfo(models.Model):
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    address = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Contact Information"

    def __str__(self):
        return "Global Contact Information"

class Page(models.Model):
    PAGE_TYPES = [
        ('aboutus', 'About Us'),
        ('privacy', 'Privacy Policy'),
        ('terms', 'Terms & Conditions'),
    ]

    title = models.CharField(max_length=150)
    type = models.CharField(max_length=20, choices=PAGE_TYPES, unique=True)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
