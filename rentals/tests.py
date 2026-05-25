from django.test import TestCase, Client
from django.contrib.auth.models import User
from rentals.models import Brand, Vehicle, Booking
from decimal import Decimal
from datetime import date, timedelta

class RentalSystemTestCase(TestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(username='test_user', password='password123', email='test@example.com')
        self.staff_user = User.objects.create_user(username='staff_user', password='password123', email='staff@example.com', is_staff=True)
        
        # Create a brand
        self.brand = Brand.objects.create(name='Tesla')
        
        # Create a vehicle
        self.vehicle = Vehicle.objects.create(
            title='Model Y',
            brand=self.brand,
            overview='A premium electric SUV.',
            price_per_day=Decimal('150.00'),
            fuel_type='Electric',
            model_year=2025,
            seating_capacity=5,
            air_conditioner=True,
            power_steering=True
        )

    def test_brand_creation(self):
        self.assertEqual(self.brand.name, 'Tesla')
        self.assertEqual(str(self.brand), 'Tesla')

    def test_vehicle_creation(self):
        self.assertEqual(self.vehicle.title, 'Model Y')
        self.assertEqual(self.vehicle.price_per_day, Decimal('150.00'))
        self.assertEqual(str(self.vehicle), 'Tesla Model Y (2025)')

    def test_booking_creation_and_number_generation(self):
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        booking = Booking.objects.create(
            user=self.user,
            vehicle=self.vehicle,
            from_date=today,
            to_date=tomorrow,
            total_price=Decimal('300.00')
        )
        
        self.assertIsNotNone(booking.booking_number)
        self.assertTrue(booking.booking_number.startswith('BK'))
        self.assertEqual(booking.status, 'Pending')
        self.assertEqual(booking.total_price, Decimal('300.00'))

    def test_admin_dashboard_access_control(self):
        client = Client()
        
        # Test anonymous access redirects or fails
        response = client.get('/admin-dashboard/')
        self.assertEqual(response.status_code, 302) # Should redirect to home or login
        
        # Test standard logged-in user access
        client.login(username='test_user', password='password123')
        response = client.get('/admin-dashboard/')
        self.assertEqual(response.status_code, 302) # Should redirect to home with access error message
        client.logout()

        # Test staff user access
        client.login(username='staff_user', password='password123')
        response = client.get('/admin-dashboard/')
        self.assertEqual(response.status_code, 200) # Access allowed
