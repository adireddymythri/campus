import os
import django
import sys

# Setup
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusmart.settings')
django.setup()

from marketplace.models import User

username = 'admin_akhil'
password = 'password123'

if not User.objects.filter(username=username).exists():
    # create_superuser sets is_staff and is_superuser to True
    user = User.objects.create_superuser(
        username=username,
        email='admin@example.com',
        password=password
    )
    user.role = 'admin' # Setting your custom role field
    user.is_verified = True
    user.save()
    print(f"Admin created! Login with: {username} / {password}")
else:
    print("User already exists.")