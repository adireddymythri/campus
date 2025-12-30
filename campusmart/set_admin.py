import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusmart.settings')

django.setup()

# Use the standard Django User model
from django.contrib.auth.models import User

# Get the first user or create one if none exist
user = User.objects.first()
if user:
    user.is_staff = True      # Allows login to /admin
    user.is_superuser = True  # Allows seeing/editing all models
    user.is_active = True     # Ensures account is not disabled
    user.save()
    print(f'User "{user.username}" has been granted full Admin/Superuser permissions.')
else:
    print('No users found in the database. Please run create_admin.py instead.')