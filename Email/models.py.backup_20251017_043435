from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Email(models.Model):
    FOLDER_CHOICES = [
        ('inbox', 'Inbox'),
        ('sent', 'Sent'),
        ('draft', 'Draft'),
        ('trash', 'Trash'),
    ]

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_emails', null=True, blank=True)
    sender_email = models.EmailField()
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_emails', null=True, blank=True)
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)
    folder = models.CharField(max_length=20, choices=FOLDER_CHOICES, default='inbox')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - From: {self.sender_email}"

class EmailAttachment(models.Model):
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='email_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename
