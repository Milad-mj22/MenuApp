from django.db import models

# Create your models here.

# seketalamanager/api/models.py
import secrets
from django.db import models



class APIKey(models.Model):
    key = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.key[:8]}..."
    
    @classmethod
    def generate(cls, name):
        """ساخت یک API Key جدید"""
        return cls.objects.create(
            key=secrets.token_urlsafe(32),
            name=name
        )

