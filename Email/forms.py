from django import forms
from .models import Email, EmailAttachment

class EmailForm(forms.ModelForm):
    class Meta:
        model = Email
        fields = ['recipient_email', 'subject', 'body']
        widgets = {
            'recipient_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'recipient@example.com'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter subject'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Type your message here...'
            }),
        }
        labels = {
            'recipient_email': 'To:',
            'subject': 'Subject:',
            'body': 'Message:',
        }

class EmailAttachmentForm(forms.ModelForm):
    class Meta:
        model = EmailAttachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
