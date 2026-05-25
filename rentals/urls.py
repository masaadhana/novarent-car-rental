from django.urls import path
from . import views

urlpatterns = [
    # Customer facing routes
    path('', views.home, name='home'),
    path('cars/', views.car_list, name='car_list'),
    path('cars/<int:car_id>/', views.car_details, name='car_details'),
    path('cars/<int:car_id>/book/', views.book_car, name='book_car'),
    path('cars/<int:car_id>/check-availability/', views.check_availability, name='check_availability'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/update-profile/', views.update_profile, name='update_profile'),
    path('dashboard/change-password/', views.change_password, name='change_password'),
    path('dashboard/submit-testimonial/', views.submit_testimonial, name='submit_testimonial'),
    path('dashboard/cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    path('contact/', views.contact, name='contact'),
    path('about/', views.about_view, name='about'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('terms/', views.terms_view, name='terms'),
    path('subscribe/', views.subscribe, name='subscribe'),

    # Admin Panel routes
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/booking-action/<int:booking_id>/<str:action>/', views.admin_booking_action, name='admin_booking_action'),
    path('admin-dashboard/toggle-testimonial/<int:testimonial_id>/', views.toggle_testimonial, name='toggle_testimonial'),
    path('admin-dashboard/mark-query-read/<int:query_id>/', views.mark_query_read, name='mark_query_read'),
    path('admin-dashboard/update-contact-settings/', views.update_contact_settings, name='update_contact_settings'),
    
    # Brands CRUD
    path('admin-dashboard/brands/add/', views.add_brand, name='add_brand'),
    path('admin-dashboard/brands/edit/<int:brand_id>/', views.edit_brand, name='edit_brand'),
    path('admin-dashboard/brands/delete/<int:brand_id>/', views.delete_brand, name='delete_brand'),
    
    # Vehicles CRUD
    path('admin-dashboard/cars/add/', views.add_vehicle, name='add_vehicle'),
    path('admin-dashboard/cars/edit/<int:car_id>/', views.edit_vehicle, name='edit_vehicle'),
    path('admin-dashboard/cars/delete/<int:car_id>/', views.delete_vehicle, name='delete_vehicle'),
    
    # Pages Editing
    path('admin-dashboard/pages/edit/<int:page_id>/', views.edit_page, name='edit_page'),
]
