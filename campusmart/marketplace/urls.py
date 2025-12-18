from django.urls import path
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.user_login, name='login'),

    # User dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user-details/', views.user_details, name='user_details'),
    path('update_user/<int:user_id>/', views.update_user_status, name='update_user_status'),

    # Product management
    path('upload-product/', views.upload_product, name='upload_product'),
    path('product/<uuid:product_id>/', views.product_details, name='product_details'),
    path('update-product-status/', views.update_product_status, name='update_product_status'),
    path('admin/remove-product/<int:product_id>/', views.remove_product, name='remove_product'),

    # Chat system
    path('chat/', views.chat_system, name='chat_system'),
    path('chat/<int:product_id>/', views.chat_system, name='chat_product'),
    path('send-message/', views.send_message, name='send_message'),

    # Admin user actions
    path('verify-user/<int:user_id>/', views.verify_user, name='verify_user'),
    path('block-user/<int:user_id>/', views.block_user, name='block_user'),
    path('reject-user/<int:user_id>/', views.reject_user, name='reject_user'),

    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/verify_user/<int:user_id>/', views.verify_user, name='verify_user'),
    path('admin/block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('logout/', views.user_logout, name='logout'),

    
  
]
