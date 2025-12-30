from django.urls import path
from . import views

urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

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
    path('api/favorite/toggle/<uuid:product_id>/', views.toggle_favorite, name='toggle_favorite'),

    # Chat system
    path('chat/', views.chat_system, name='chat_system'),
    path('chat/<int:product_id>/', views.chat_system, name='chat_product'),
    path('send-message/', views.send_message, name='send_message'),
    path('api/messages/<uuid:conversation_id>/', views.get_messages, name='get_messages'),
    path('profile/update/', views.update_profile, name='update_profile'),

    # Admin user actions
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('verify-user/<int:user_id>/', views.verify_user, name='verify_user'),
    path('block-user/<int:user_id>/', views.block_user, name='block_user'),
    path('reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
    
    # Admin API endpoints
    path('api/admin/users/', views.get_users_data, name='get_users_data'),
    path('api/admin/products/', views.get_products_data, name='get_products_data'),
    path('api/admin/stats/', views.get_dashboard_stats, name='get_dashboard_stats'),
    
    # Check if these view functions exist before uncommenting
    path('api/admin/category/add/', views.add_category, name='add_category'),
    path('api/admin/category/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('api/admin/settings/', views.get_global_settings, name='get_global_settings'),
    path('api/admin/settings/update/', views.update_global_settings, name='update_global_settings'),
    path('api/admin/product/approve/<uuid:product_id>/', views.admin_approve_product, name='admin_approve_product'),
    path('api/admin/product/block/<uuid:product_id>/', views.admin_block_product, name='admin_block_product'),

    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    path('admin/verify_user/<int:user_id>/', views.verify_user, name='verify_user'),
    path('admin/block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('logout/', views.user_logout, name='logout'),

    
  
]
