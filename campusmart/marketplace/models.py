from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid

# --- 1. USER MODEL ---
# Using AbstractUser allows you to add custom fields while keeping Django's login system
class User(AbstractUser):
    USER_ROLES = (('user', 'User'), ('admin', 'Admin'))
    
    role = models.CharField(max_length=10, choices=USER_ROLES, default='user')
    name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    # Campus Details
    college_name = models.CharField(max_length=255, blank=True, null=True)
    college_id = models.CharField(max_length=50, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    hostel_block = models.CharField(max_length=50, blank=True, null=True)
    room_no = models.CharField(max_length=20, blank=True, null=True)
    
    is_admin_user = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name if self.name else self.username

# --- 2. CATEGORY MODEL ---
class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

# --- 6. GLOBAL SETTINGS MODEL ---
class GlobalSettings(models.Model):
    auto_approve_products = models.BooleanField(default=True)
    require_user_verification = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Global Settings"

    class Meta:
        verbose_name_plural = "Global Settings"

# --- 3. PRODUCT MODEL ---
class Product(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('in_progress', 'In Progress'),
        ('blocked', 'Blocked')
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Use settings.AUTH_USER_MODEL to refer to your custom User model
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products_sold')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='products_bought')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

# --- 4. CONVERSATION MODEL ---
class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_conversations')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'buyer', 'seller']

# --- 5. MESSAGE MODEL ---
class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender.username} at {self.timestamp}"

# --- 6. FAVORITE MODEL ---
class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} likes {self.product.title}"