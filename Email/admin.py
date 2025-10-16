from django.contrib import admin
from .models import Email, EmailAttachment

# Register your models here.

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['subject', 'sender_email', 'recipient_email', 'folder', 'is_read', 'is_starred', 'created_at', 'sent_at']
    list_filter = ['folder', 'is_read', 'is_starred', 'created_at']
    search_fields = ['subject', 'sender_email', 'recipient_email', 'body']
    readonly_fields = ['created_at', 'sent_at']

@admin.register(EmailAttachment)
class EmailAttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'email', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['filename']
