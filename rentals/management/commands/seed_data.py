from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rentals.models import Brand, Vehicle, Booking, Testimonial, ContactInfo, Page, ContactQuery, Subscriber
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seeds the database with realistic initial data, pages, contact info, and an admin user'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # 1. Create Admin User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@NovaRent.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user: admin / admin123'))
        else:
            self.stdout.write('Admin user "admin" already exists.')

        # 2. Create Test Users
        user1, created1 = User.objects.get_or_create(
            username='john_doe',
            defaults={
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        if created1:
            user1.set_password('password123')
            user1.save()
            self.stdout.write('Created test user: john_doe / password123')

        user2, created2 = User.objects.get_or_create(
            username='jane_smith',
            defaults={
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith'
            }
        )
        if created2:
            user2.set_password('password123')
            user2.save()
            self.stdout.write('Created test user: jane_smith / password123')

        # 3. Create Brands
        brands = {}
        brand_names = ['Tesla', 'Porsche', 'BMW', 'Audi', 'Mercedes-Benz', 'Hyundai']
        for name in brand_names:
            brand, created = Brand.objects.get_or_create(name=name)
            brands[name] = brand
            if created:
                self.stdout.write(f"Created Brand: {name}")

        # 4. Create Vehicles
        vehicles_data = [
            {
                'title': 'Model S Plaid',
                'brand': brands['Tesla'],
                'overview': 'The Tesla Model S Plaid is an all-electric flagship luxury sedan featuring peak power of 1,020 horsepower, tri-motor all-wheel drive, and 0-60 mph acceleration in 1.99 seconds. Experience state-of-the-art Autopilot tech and high-end gaming computers onboard.',
                'price_per_day': Decimal('249.00'),
                'fuel_type': 'Electric',
                'model_year': 2025,
                'seating_capacity': 5,
                'air_conditioner': True,
                'power_door_locks': True,
                'anti_lock_braking': True,
                'brake_assist': True,
                'power_steering': True,
                'driver_airbag': True,
                'passenger_airbag': True,
                'power_windows': True,
                'cd_player': False,
                'central_locking': True,
                'crash_sensor': True,
                'leather_seats': True,
            },
            {
                'title': '911 Carrera GTS',
                'brand': brands['Porsche'],
                'overview': 'Pure sports car design meets precision engineering. The Porsche 911 Carrera GTS delivers a twin-turbocharged boxer engine producing 473 horsepower. Features custom sports exhaust, dynamic chassis control, and classic cockpit aesthetics for the ultimate drive.',
                'price_per_day': Decimal('349.00'),
                'fuel_type': 'Petrol',
                'model_year': 2024,
                'seating_capacity': 4,
                'air_conditioner': True,
                'power_door_locks': True,
                'anti_lock_braking': True,
                'brake_assist': True,
                'power_steering': True,
                'driver_airbag': True,
                'passenger_airbag': True,
                'power_windows': True,
                'cd_player': False,
                'central_locking': True,
                'crash_sensor': True,
                'leather_seats': True,
            },
            {
                'title': 'M8 Competition Gran Coupe',
                'brand': brands['BMW'],
                'overview': 'The BMW M8 Competition Gran Coupe is an ultra-premium four-door luxury sports car. Driven by a 4.4L twin-turbo V8 outputting 617 horsepower, it couples executive class seating comfort with brutal, racetrack-ready speed.',
                'price_per_day': Decimal('299.00'),
                'fuel_type': 'Petrol',
                'model_year': 2025,
                'seating_capacity': 5,
                'air_conditioner': True,
                'power_door_locks': True,
                'anti_lock_braking': True,
                'brake_assist': True,
                'power_steering': True,
                'driver_airbag': True,
                'passenger_airbag': True,
                'power_windows': True,
                'cd_player': True,
                'central_locking': True,
                'crash_sensor': True,
                'leather_seats': True,
            },
            {
                'title': 'e-tron GT',
                'brand': brands['Audi'],
                'overview': 'The Audi e-tron GT is an elegant grand tourer combining progressive styling with electric utility. Dual synchronous electric motors provide all-wheel drive stability. Charge up to 80% in 22 minutes on ultra-fast networks.',
                'price_per_day': Decimal('199.00'),
                'fuel_type': 'Electric',
                'model_year': 2024,
                'seating_capacity': 5,
                'air_conditioner': True,
                'power_door_locks': True,
                'anti_lock_braking': True,
                'brake_assist': True,
                'power_steering': True,
                'driver_airbag': True,
                'passenger_airbag': True,
                'power_windows': True,
                'cd_player': False,
                'central_locking': True,
                'crash_sensor': True,
                'leather_seats': True,
            },
            {
                'title': 'G 63 AMG Wagon',
                'brand': brands['Mercedes-Benz'],
                'overview': 'The iconic G-Wagon is an off-road military-grade luxury SUV. The G63 features a handcrafted AMG 4.0L V8 twin-turbo engine delivering 577 horsepower. Outfitted with triple locking differentials, side-pipe exhausts, and luxury massage seats.',
                'price_per_day': Decimal('399.00'),
                'fuel_type': 'Petrol',
                'model_year': 2025,
                'seating_capacity': 5,
                'air_conditioner': True,
                'power_door_locks': True,
                'anti_lock_braking': True,
                'brake_assist': True,
                'power_steering': True,
                'driver_airbag': True,
                'passenger_airbag': True,
                'power_windows': True,
                'cd_player': True,
                'central_locking': True,
                'crash_sensor': True,
                'leather_seats': True,
            },
            {
                'title': 'IONIQ 5 N',
                'brand': brands['Hyundai'],
                'overview': 'Experience high-performance electric track capability in a daily crossover package. The IONIQ 5 N features simulated gearshifts, 641 horsepower in Boost mode, custom drift optimizer systems, and sport bucket seats.',
                'price_per_day': Decimal('149.00'),
                'fuel_type': 'Hybrid',
                'model_year': 2025,
                'seating_capacity': 5,
                'air_conditioner': True,
                'power_door_locks': True,
                'anti_lock_braking': True,
                'brake_assist': True,
                'power_steering': True,
                'driver_airbag': True,
                'passenger_airbag': True,
                'power_windows': True,
                'cd_player': False,
                'central_locking': True,
                'crash_sensor': True,
                'leather_seats': True,
            }
        ]

        for data in vehicles_data:
            vehicle, created = Vehicle.objects.get_or_create(
                title=data['title'],
                brand=data['brand'],
                defaults=data
            )
            if created:
                self.stdout.write(f"Created Vehicle: {vehicle}")

        # 5. Create Testimonials
        testimonials_data = [
            {
                'user': user1,
                'testimonial_text': 'I rented the Tesla Model S Plaid for my anniversary weekend. The vehicle was in immaculate condition and the performance was absolutely shocking. The booking and checkout flow on the site was seamless! Will definitely rent again.',
                'status': 'Active'
            },
            {
                'user': user2,
                'testimonial_text': 'Excellent fleet selection. The AMG G-Wagon was clean, loaded with accessories, and ready on time. The custom admin dashboard makes approvals lightning fast. Outstanding service!',
                'status': 'Active'
            }
        ]
        for t_data in testimonials_data:
            t, created = Testimonial.objects.get_or_create(
                user=t_data['user'],
                testimonial_text=t_data['testimonial_text'],
                defaults={'status': t_data['status']}
            )
            if created:
                self.stdout.write(f"Created Testimonial by {t.user.username}")

        # 6. Global Contact Information
        contact_info, created = ContactInfo.objects.get_or_create(
            id=1,
            defaults={
                'email': 'support@NovaRent.com',
                'phone': '+1 (555) 234-5678',
                'address': '100 Innovation Way, Suite 400\nNew York, NY 10001'
            }
        )
        if created:
            self.stdout.write("Created Global Contact Information settings.")

        # 7. Static Pages
        Page.objects.get_or_create(
            type='aboutus',
            defaults={
                'title': 'About NovaRent',
                'content': 'Welcome to NovaRent, a premier luxury and performance vehicle rental solution established in 2026. Our core objective is to deliver unparalleled convenience and sophistication. By leveraging robust server automation, we manage vehicle availabilities, profiles, and requests efficiently. Whether you desire high-speed sports vehicles or eco-conscious electric cars, NovaRent provides the premium platform for your journey.'
            }
        )
        Page.objects.get_or_create(
            type='privacy',
            defaults={
                'title': 'Privacy Policy',
                'content': 'NovaRent is committed to safeguarding your data. We operate secure session handlers and database schemas. Credit card information and payment details are never saved locally. We only collect essential customer identifiers necessary for authentication, profile updates, and booking records. Check our security dashboard for access settings.'
            }
        )
        Page.objects.get_or_create(
            type='terms',
            defaults={
                'title': 'Terms & Conditions',
                'content': 'All vehicle rentals are governed by local driving regulations. Renters must present a valid driver license, satisfy standard age requirements, and verify secondary insurance coverages. Pick up and drop off dates must be respected. Late checkouts will incur standard per-hour fees. Cancel booking requests are allowed for pending reservations.'
            }
        )
        self.stdout.write(self.style.SUCCESS('Static content pages verified.'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
