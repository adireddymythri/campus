#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

# Add the campusmart directory to the Python path so Django can find the settings module
BASE_DIR = Path(__file__).resolve().parent
campusmart_dir = BASE_DIR / 'campusmart'
if campusmart_dir.exists():
    if str(campusmart_dir) not in sys.path:
        sys.path.insert(0, str(campusmart_dir))


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusmart.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
