import secrets

from django.contrib import admin

from api.models import APIKey

# Register your models here.
@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'key_preview', 'is_active', 'created_at']
    readonly_fields = ['key', 'created_at']
    
    def key_preview(self, obj):
        return f"{obj.key[:12]}..."
    key_preview.short_description = 'Key'
    
    def save_model(self, request, obj, form, change):
        if not obj.key:
            obj.key = secrets.token_urlsafe(32)
        super().save_model(request, obj, form, change)