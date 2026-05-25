from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime
from .models import Brand, Vehicle, Booking, Testimonial, ContactQuery, Subscriber, ContactInfo, Page

# --- Helper function for admin staff restriction ---
def is_staff_user(user):
    return user.is_authenticated and user.is_staff

# --- Client Views ---

def home(request):
    brands = Brand.objects.all().order_by('name')
    cars = Vehicle.objects.all().order_by('-created_at')[:6]
    testimonials = Testimonial.objects.filter(status='Active').order_by('-created_at')
    
    # Pre-populate contact settings if missing
    contact_config = ContactInfo.objects.first()
    if not contact_config:
        contact_config = ContactInfo.objects.create(
            email="support@NovaRent.com",
            phone="+1 (555) 234-5678",
            address="100 Innovation Way, Suite 400\nNew York, NY 10001"
        )
        
    return render(request, 'rentals/home.html', {
        'brands': brands,
        'cars': cars,
        'testimonials': testimonials,
        'contact_info': contact_config
    })

def car_list(request):
    brands = Brand.objects.all().order_by('name')
    vehicles = Vehicle.objects.all()

    # Search & Filter Parameters
    q = request.GET.get('q', '')
    brand_id = request.GET.get('brand', '')
    fuel = request.GET.get('fuel', '')
    seats = request.GET.get('seats', '')
    price = request.GET.get('price', '')

    if q:
        vehicles = vehicles.filter(Q(title__icontains=q) | Q(overview__icontains=q))
    if brand_id:
        vehicles = vehicles.filter(brand_id=brand_id)
    if fuel:
        vehicles = vehicles.filter(fuel_type=fuel)
    if seats:
        vehicles = vehicles.filter(seating_capacity__gte=seats)
    if price:
        vehicles = vehicles.filter(price_per_day__lte=price)

    return render(request, 'rentals/car_list.html', {
        'cars': vehicles.order_by('-created_at'),
        'brands': brands,
        'query_q': q,
        'query_brand': brand_id,
        'query_fuel': fuel,
        'query_seats': seats,
        'query_price': price,
    })

def car_details(request, car_id):
    car = get_object_or_404(Vehicle, id=car_id)
    return render(request, 'rentals/car_details.html', {'car': car})

def check_availability(request, car_id):
    car = get_object_or_404(Vehicle, id=car_id)
    from_date_str = request.GET.get('from_date', '')
    to_date_str = request.GET.get('to_date', '')

    if not from_date_str or not to_date_str:
        return JsonResponse({'available': False, 'error': 'Missing dates'})

    try:
        from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
        to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'available': False, 'error': 'Invalid date format'})

    # Query overlapping bookings that are either approved or pending
    overlapping_bookings = Booking.objects.filter(
        vehicle=car,
        status__in=['Approved', 'Pending']
    ).filter(
        from_date__lte=to_date,
        to_date__gte=from_date
    )

    is_available = not overlapping_bookings.exists()
    return JsonResponse({'available': is_available})

def book_car(request, car_id):
    if not request.user.is_authenticated:
        messages.error(request, "Please sign in to make a reservation.")
        return redirect('login')

    car = get_object_or_404(Vehicle, id=car_id)
    
    if request.method == 'POST':
        from_date_str = request.POST.get('from_date')
        to_date_str = request.POST.get('to_date')
        message = request.POST.get('message', '')

        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, "Please enter valid dates.")
            return redirect('car_details', car_id=car.id)

        if from_date > to_date:
            messages.error(request, "Drop-off date cannot be earlier than Pick-up date.")
            return redirect('car_details', car_id=car.id)

        # Check overlapping bookings again on server side
        overlapping = Booking.objects.filter(
            vehicle=car,
            status__in=['Approved', 'Pending']
        ).filter(
            from_date__lte=to_date,
            to_date__gte=from_date
        )

        if overlapping.exists():
            messages.error(request, "The vehicle is already booked for the selected dates.")
            return redirect('car_details', car_id=car.id)

        # Calculate Price
        days = (to_date - from_date).days + 1
        total_price = car.price_per_day * days

        # Save booking
        Booking.objects.create(
            user=request.user,
            vehicle=car,
            from_date=from_date,
            to_date=to_date,
            message=message,
            total_price=total_price,
            status='Pending'
        )

        messages.success(request, f"Your reservation request for {car.title} has been submitted successfully!")
        return redirect('user_dashboard')

    return redirect('car_details', car_id=car.id)

# --- Authentication Views ---

def user_login(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            next_url = request.GET.get('next', 'user_dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'rentals/auth.html', {'tab': 'login'})

def user_register(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('login')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('login')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email address already registered.")
            return redirect('login')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        login(request, user)
        messages.success(request, "Registration successful! Welcome to NovaRent.")
        return redirect('user_dashboard')

    return redirect('login')

def user_logout(request):
    logout(request)
    messages.success(request, "Successfully logged out.")
    return redirect('home')

# --- User Dashboard Views ---

def user_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'rentals/user_dashboard.html', {
        'bookings': bookings
    })

def update_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        user = request.user
        
        # Check if email is used by another user
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, "Email address is already in use.")
            return redirect('/dashboard/#profile')

        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('/dashboard/#profile')

    return redirect('user_dashboard')

def change_password(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        old_pass = request.POST.get('old_password')
        new_pass = request.POST.get('new_password')
        confirm_new = request.POST.get('confirm_new_password')

        user = request.user
        
        if not check_password(old_pass, user.password):
            messages.error(request, "Incorrect current password.")
            return redirect('/dashboard/#security')

        if new_pass != confirm_new:
            messages.error(request, "New passwords do not match.")
            return redirect('/dashboard/#security')

        user.set_password(new_pass)
        user.save()
        # Log user back in as changing password logs them out
        login(request, user)

        messages.success(request, "Password updated successfully.")
        return redirect('/dashboard/#security')

    return redirect('user_dashboard')

def submit_testimonial(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        text = request.POST.get('testimonial_text')
        
        Testimonial.objects.create(
            user=request.user,
            testimonial_text=text,
            status='Inactive'
        )

        messages.success(request, "Thank you! Your testimonial has been submitted for review.")
        return redirect('/dashboard/#testimonial')

    return redirect('user_dashboard')

def cancel_booking(request, booking_id):
    if not request.user.is_authenticated:
        return redirect('login')

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status == 'Pending':
        booking.status = 'Cancelled'
        booking.save()
        messages.success(request, f"Booking {booking.booking_number} was cancelled.")
    else:
        messages.error(request, "Only pending bookings can be cancelled.")

    return redirect('/dashboard/#bookings')

# --- Static Information / Forms ---

def contact(request):
    contact_config = ContactInfo.objects.first()
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        ContactQuery.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )
        messages.success(request, "Thank you! Your inquiry was sent successfully. We will contact you soon.")
        return redirect('contact')

    return render(request, 'rentals/contact.html', {
        'contact_info': contact_config
    })

def about_view(request):
    page, created = Page.objects.get_or_create(type='aboutus', defaults={
        'title': 'About NovaRent',
        'content': 'NovaRent is a premium car rental platform founded in 2026. We provide dynamic booking, automated vehicle scheduling, and unmatched luxury vehicle catalog choices.'
    })
    return render(request, 'rentals/page.html', {'page': page})

def privacy_view(request):
    page, created = Page.objects.get_or_create(type='privacy', defaults={
        'title': 'Privacy Policy',
        'content': 'Your privacy is valuable to us. This policy details our secure operations regarding databases, transaction records, and user session management.'
    })
    return render(request, 'rentals/page.html', {'page': page})

def terms_view(request):
    page, created = Page.objects.get_or_create(type='terms', defaults={
        'title': 'Terms & Conditions',
        'content': 'By accessing or renting vehicles through NovaRent, you agree to our driver terms, age requirements, insurance regulations, and standard booking policies.'
    })
    return render(request, 'rentals/page.html', {'page': page})

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            if Subscriber.objects.filter(email=email).exists():
                messages.warning(request, "You are already subscribed to our newsletter.")
            else:
                Subscriber.objects.create(email=email)
                messages.success(request, "Thank you for subscribing to our newsletter!")
        
        # Redirect back
        referer = request.META.get('HTTP_REFERER', 'home')
        return redirect(referer)
    return redirect('home')

# --- Custom Admin Dashboard Views (Staff Restricted) ---

def admin_dashboard(request):
    if not is_staff_user(request.user):
        messages.error(request, "Access Denied. Administrator credentials required.")
        return redirect('home')

    # Gather data counts
    stats = {
        'vehicles': Vehicle.objects.count(),
        'bookings': Booking.objects.count(),
        'users': User.objects.filter(is_staff=False).count(),
        'subscribers': Subscriber.objects.count(),
    }

    # Lists
    pending_bookings = Booking.objects.filter(status='Pending').order_by('-created_at')
    all_bookings = Booking.objects.all().order_by('-created_at')
    vehicles = Vehicle.objects.all().order_by('-created_at')
    brands = Brand.objects.all().order_by('name')
    testimonials = Testimonial.objects.all().order_by('-created_at')
    queries = ContactQuery.objects.all().order_by('-created_at')
    subscribers = Subscriber.objects.all().order_by('-created_at')
    pages = Page.objects.all()
    
    contact_config = ContactInfo.objects.first()

    return render(request, 'rentals/admin_dashboard.html', {
        'stats': stats,
        'pending_bookings': pending_bookings,
        'bookings': all_bookings,
        'vehicles': vehicles,
        'brands': brands,
        'testimonials': testimonials,
        'queries': queries,
        'subscribers': subscribers,
        'pages': pages,
        'contact_config': contact_config
    })

def admin_booking_action(request, booking_id, action):
    if not is_staff_user(request.user):
        messages.error(request, "Access Denied.")
        return redirect('home')

    booking = get_object_or_404(Booking, id=booking_id)
    if action in ['Approve', 'Reject', 'Cancel']:
        if action == 'Approve':
            booking.status = 'Approved'
        elif action == 'Reject':
            booking.status = 'Rejected'
        elif action == 'Cancel':
            booking.status = 'Cancelled'
        
        booking.save()
        messages.success(request, f"Booking {booking.booking_number} status updated to {booking.status}.")
    
    return redirect('/admin-dashboard/#bookings')

def toggle_testimonial(request, testimonial_id):
    if not is_staff_user(request.user):
        messages.error(request, "Access Denied.")
        return redirect('home')

    t = get_object_or_404(Testimonial, id=testimonial_id)
    t.status = 'Active' if t.status == 'Inactive' else 'Inactive'
    t.save()
    
    messages.success(request, f"Testimonial status set to {t.status}.")
    return redirect('/admin-dashboard/#testimonials')

def mark_query_read(request, query_id):
    if not is_staff_user(request.user):
        messages.error(request, "Access Denied.")
        return redirect('home')

    q = get_object_or_404(ContactQuery, id=query_id)
    q.status = 'Read'
    q.save()
    
    messages.success(request, "Contact query marked as read.")
    return redirect('/admin-dashboard/#queries')

def update_contact_settings(request):
    if not is_staff_user(request.user):
        messages.error(request, "Access Denied.")
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        config = ContactInfo.objects.first()
        if not config:
            ContactInfo.objects.create(email=email, phone=phone, address=address)
        else:
            config.email = email
            config.phone = phone
            config.address = address
            config.save()

        messages.success(request, "Global contact settings updated successfully.")
    return redirect('/admin-dashboard/#config')

# --- Brands CRUD ---

def add_brand(request):
    if not is_staff_user(request.user):
        messages.error(request, "Access Denied.")
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            if Brand.objects.filter(name__iexact=name).exists():
                messages.error(request, "A brand with that name already exists.")
            else:
                Brand.objects.create(name=name)
                messages.success(request, f"Brand '{name}' added successfully.")
                return redirect('/admin-dashboard/#brands')

    return render(request, 'rentals/admin_form.html', {
        'form_type': 'brand',
        'form_title': 'Add New Brand',
        'back_url': '/admin-dashboard/#brands'
    })

def edit_brand(request, brand_id):
    if not is_staff_user(request.user):
        messages.error(request, "Access Denied.")
        return redirect('home')

    brand = get_object_or_404(Brand, id=brand_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            brand.name = name
            brand.save()
            messages.success(request, f"Brand updated to '{name}'.")
            return redirect('/admin-dashboard/#brands')

    return render(request, 'rentals/admin_form.html', {
        'form_type': 'brand',
        'form_title': f"Edit Brand: {brand.name}",
        'brand': brand,
        'back_url': '/admin-dashboard/#brands'
    })

def delete_brand(request, brand_id):
    if not is_staff_user(request.user):
        messages.error(request, "Access Denied.")
        return redirect('home')

    brand = get_object_or_404(Brand, id=brand_id)
    name = brand.name
    brand.delete()
    messages.success(request, f"Brand '{name}' and all associated vehicles deleted.")
    return redirect('/admin-dashboard/#brands')

# --- Vehicles CRUD ---

def add_vehicle(request):
    if not is_staff_user(request.user):
        messages.error(request, "Access Denied.")
        return redirect('home')

    brands = Brand.objects.all().order_by('name')

    if request.method == 'POST':
        title = request.POST.get('title')
        brand_id = request.POST.get('brand')
        overview = request.POST.get('overview')
        price_per_day = request.POST.get('price_per_day')
        fuel_type = request.POST.get('fuel_type')
        model_year = request.POST.get('model_year')
        seating_capacity = request.POST.get('seating_capacity')
        
        # Files
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')

        # Accessories
        air_conditioner = 'air_conditioner' in request.POST
        power_door_locks = 'power_door_locks' in request.POST
        anti_lock_braking = 'anti_lock_braking' in request.POST
        brake_assist = 'brake_assist' in request.POST
        power_steering = 'power_steering' in request.POST
        driver_airbag = 'driver_airbag' in request.POST
        passenger_airbag = 'passenger_airbag' in request.POST
        power_windows = 'power_windows' in request.POST
        cd_player = 'cd_player' in request.POST
        central_locking = 'central_locking' in request.POST
        crash_sensor = 'crash_sensor' in request.POST
        leather_seats = 'leather_seats' in request.POST

        brand = get_object_or_404(Brand, id=brand_id)
        
        Vehicle.objects.create(
            title=title,
            brand=brand,
            overview=overview,
            price_per_day=price_per_day,
            fuel_type=fuel_type,
            model_year=model_year,
            seating_capacity=seating_capacity,
            image1=image1,
            image2=image2,
            image3=image3,
            image4=image4,
            air_conditioner=air_conditioner,
            power_door_locks=power_door_locks,
            anti_lock_braking=anti_lock_braking,
            brake_assist=brake_assist,
            power_steering=power_steering,
            driver_airbag=driver_airbag,
            passenger_airbag=passenger_airbag,
            power_windows=power_windows,
            cd_player=cd_player,
            central_locking=central_locking,
            crash_sensor=crash_sensor,
            leather_seats=leather_seats
        )

        messages.success(request, f"Vehicle '{brand.name} {title}' added to fleet.")
        return redirect('/admin-dashboard/#vehicles')

    return render(request, 'rentals/admin_form.html', {
        'form_type': 'vehicle',
        'form_title': 'Add New Vehicle',
        'brands': brands,
        'back_url': '/admin-dashboard/#vehicles'
    })

def edit_vehicle(request, car_id):
    if not is_staff_user(request.user):
        messages.error(request, "Access Denied.")
        return redirect('home')

    car = get_object_or_404(Vehicle, id=car_id)
    brands = Brand.objects.all().order_by('name')

    if request.method == 'POST':
        title = request.POST.get('title')
        brand_id = request.POST.get('brand')
        overview = request.POST.get('overview')
        price_per_day = request.POST.get('price_per_day')
        fuel_type = request.POST.get('fuel_type')
        model_year = request.POST.get('model_year')
        seating_capacity = request.POST.get('seating_capacity')
        
        # Files update only if new uploaded
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')

        # Accessories
        air_conditioner = 'air_conditioner' in request.POST
        power_door_locks = 'power_door_locks' in request.POST
        anti_lock_braking = 'anti_lock_braking' in request.POST
        brake_assist = 'brake_assist' in request.POST
        power_steering = 'power_steering' in request.POST
        driver_airbag = 'driver_airbag' in request.POST
        passenger_airbag = 'passenger_airbag' in request.POST
        power_windows = 'power_windows' in request.POST
        cd_player = 'cd_player' in request.POST
        central_locking = 'central_locking' in request.POST
        crash_sensor = 'crash_sensor' in request.POST
        leather_seats = 'leather_seats' in request.POST

        brand = get_object_or_404(Brand, id=brand_id)

        car.title = title
        car.brand = brand
        car.overview = overview
        car.price_per_day = price_per_day
        car.fuel_type = fuel_type
        car.model_year = model_year
        car.seating_capacity = seating_capacity
        
        if image1: car.image1 = image1
        if image2: car.image2 = image2
        if image3: car.image3 = image3
        if image4: car.image4 = image4

        car.air_conditioner = air_conditioner
        car.power_door_locks = power_door_locks
        car.anti_lock_braking = anti_lock_braking
        car.brake_assist = brake_assist
        car.power_steering = power_steering
        car.driver_airbag = driver_airbag
        car.passenger_airbag = passenger_airbag
        car.power_windows = power_windows
        car.cd_player = cd_player
        car.central_locking = central_locking
        car.crash_sensor = crash_sensor
        car.leather_seats = leather_seats

        car.save()
        messages.success(request, f"Vehicle '{brand.name} {title}' updated.")
        return redirect('/admin-dashboard/#vehicles')

    return render(request, 'rentals/admin_form.html', {
        'form_type': 'vehicle',
        'form_title': f"Edit Vehicle: {car.brand.name} {car.title}",
        'vehicle': car,
        'brands': brands,
        'back_url': '/admin-dashboard/#vehicles'
    })

def delete_vehicle(request, car_id):
    if not is_staff_user(request.user):
        messages.error(request, "Access Denied.")
        return redirect('home')

    car = get_object_or_404(Vehicle, id=car_id)
    title = car.title
    car.delete()
    messages.success(request, f"Vehicle '{title}' deleted from fleet.")
    return redirect('/admin-dashboard/#vehicles')

# --- Pages CRUD ---

def edit_page(request, page_id):
    if not is_staff_user(request.user):
        messages.error(request, "Access Denied.")
        return redirect('home')

    page = get_object_or_404(Page, id=page_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')

        page.title = title
        page.content = content
        page.save()

        messages.success(request, f"Page '{title}' updated successfully.")
        return redirect('/admin-dashboard/#pages')

    return render(request, 'rentals/admin_form.html', {
        'form_type': 'page',
        'form_title': f"Edit Page: {page.title}",
        'page': page,
        'back_url': '/admin-dashboard/#pages'
    })
