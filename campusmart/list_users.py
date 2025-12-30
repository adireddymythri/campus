import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusmart.settings')

django.setup()

from marketplace.models import User

users = User.objects.all()
print('Existing Users:')
for u in users:
    print(f'Username: {u.username}, Email: {u.email}, Is Admin: {u.is_admin_user}')
