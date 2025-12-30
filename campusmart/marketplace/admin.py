from django.contrib import admin
from .models import User, Category, Product, Conversation, Message

# We use a custom Admin class for User to show important fields
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_verified')
    list_filter = ('role', 'is_verified', 'is_staff')

admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Conversation)
admin.site.register(Message)