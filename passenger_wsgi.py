

import sys
import os

# تنظیم مسیر پروژه
sys.path.insert(0, '/home/seketal1/MenuApp/passenger_wsgi.py')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MenuApp.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

