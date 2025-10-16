from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from .forms import EmailForm, EmailAttachmentForm
from .models import Email, EmailAttachment
from .imap_utils import fetch_emails, setup_imap_connection

# Create your views here.

@login_required
def inbox_view(request):
    """Display inbox with received emails"""
    folder = request.GET.get('folder', 'inbox')

    if folder == 'inbox':
        emails = Email.objects.filter(recipient=request.user, folder='inbox').order_by('-created_at')
    elif folder == 'sent':
        emails = Email.objects.filter(sender=request.user, folder='sent').order_by('-sent_at')
    elif folder == 'draft':
        emails = Email.objects.filter(sender=request.user, folder='draft').order_by('-created_at')
    elif folder == 'trash':
        emails = Email.objects.filter(
            Q(sender=request.user) | Q(recipient=request.user),
            folder='trash'
        ).order_by('-created_at')
    else:
        emails = Email.objects.filter(recipient=request.user, folder='inbox').order_by('-created_at')

    # Count unread emails
    unread_count = Email.objects.filter(recipient=request.user, is_read=False, folder='inbox').count()

    context = {
        'emails': emails,
        'current_folder': folder,
        'unread_count': unread_count,
    }

    return render(request, 'email/inbox.html', context)

@login_required
def email_detail_view(request, email_id):
    """Display a single email"""
    email = get_object_or_404(Email, id=email_id)

    # Check if user has permission to view this email
    if email.recipient != request.user and email.sender != request.user:
        messages.error(request, "You don't have permission to view this email.")
        return redirect('inbox')

    # Mark as read if recipient is viewing
    if email.recipient == request.user and not email.is_read:
        email.is_read = True
        email.save()

    context = {
        'email': email,
    }

    return render(request, 'email/email_detail.html', context)

@login_required
def compose_email_view(request):
    """Compose and send a new email"""
    if request.method == 'POST':
        form = EmailForm(request.POST)

        if form.is_valid():
            email = form.save(commit=False)
            email.sender = request.user
            email.sender_email = request.user.email

            # Handle attachments
            files = request.FILES.getlist('attachments')

            # Check if saving as draft
            if 'save_draft' in request.POST:
                email.folder = 'draft'
                email.save()

                # Save attachments
                for file in files:
                    EmailAttachment.objects.create(
                        email=email,
                        file=file,
                        filename=file.name
                    )

                messages.success(request, 'Email saved as draft.')
                return redirect('inbox')

            # Sending the email
            try:
                # Try to find recipient user
                from django.contrib.auth.models import User
                try:
                    recipient_user = User.objects.get(email=email.recipient_email)
                    email.recipient = recipient_user
                except User.DoesNotExist:
                    email.recipient = None

                email.sent_at = timezone.now()
                email.folder = 'sent'
                email.save()

                # Save attachments
                for file in files:
                    EmailAttachment.objects.create(
                        email=email,
                        file=file,
                        filename=file.name
                    )

                # Create a copy for recipient's inbox if they're a user
                if email.recipient:
                    inbox_email = Email.objects.create(
                        sender=email.sender,
                        sender_email=email.sender_email,
                        recipient=email.recipient,
                        recipient_email=email.recipient_email,
                        subject=email.subject,
                        body=email.body,
                        sent_at=email.sent_at,
                        folder='inbox'
                    )
                    # Copy attachments
                    for attachment in email.attachments.all():
                        EmailAttachment.objects.create(
                            email=inbox_email,
                            file=attachment.file,
                            filename=attachment.filename
                        )

                # Send actual email via SMTP
                send_mail(
                    email.subject,
                    email.body,
                    email.sender_email,
                    [email.recipient_email],
                    fail_silently=False,
                )

                messages.success(request, 'Email sent successfully!')
                return redirect('inbox')

            except Exception as e:
                messages.error(request, f'Error sending email: {str(e)}')
                return redirect('compose_email')
    else:
        form = EmailForm()

    context = {
        'form': form,
    }

    return render(request, 'email/compose_email.html', context)

@login_required
def delete_email_view(request, email_id):
    """Move email to trash or delete permanently"""
    email = get_object_or_404(Email, id=email_id)

    # Check permission
    if email.recipient != request.user and email.sender != request.user:
        messages.error(request, "You don't have permission to delete this email.")
        return redirect('inbox')

    if email.folder == 'trash':
        # Permanently delete
        email.delete()
        messages.success(request, 'Email deleted permanently.')
    else:
        # Move to trash
        email.folder = 'trash'
        email.save()
        messages.success(request, 'Email moved to trash.')

    return redirect('inbox')

@login_required
def star_email_view(request, email_id):
    """Toggle star status of an email"""
    email = get_object_or_404(Email, id=email_id)

    # Check permission
    if email.recipient != request.user and email.sender != request.user:
        messages.error(request, "You don't have permission to star this email.")
        return redirect('inbox')

    email.is_starred = not email.is_starred
    email.save()

    return redirect(request.META.get('HTTP_REFERER', 'inbox'))

@login_required
def mark_as_read_view(request, email_id):
    """Mark email as read"""
    email = get_object_or_404(Email, id=email_id)

    if email.recipient == request.user:
        email.is_read = True
        email.save()

    return redirect(request.META.get('HTTP_REFERER', 'inbox'))

@login_required
def mark_as_unread_view(request, email_id):
    """Mark email as unread"""
    email = get_object_or_404(Email, id=email_id)

    if email.recipient == request.user:
        email.is_read = False
        email.save()

    return redirect(request.META.get('HTTP_REFERER', 'inbox'))

@login_required
def fetch_external_emails_view(request):
    """Fetch emails from external IMAP server"""
    if request.method == 'POST':
        # Get IMAP connection settings
        connection = setup_imap_connection(request.user)

        if not connection:
            messages.error(request, "Email connection settings not properly configured.")
            return redirect('inbox')

        try:
            # Fetch emails
            fetched = fetch_emails(
                user=request.user,
                imap_server=connection['imap_server'],
                email_address=connection['email_address'],
                password=connection['password'],
                limit=20,  # Fetch last 20 emails
                save_to_db=True
            )

            messages.success(request, f"Successfully fetched {len(fetched)} emails.")
        except Exception as e:
            messages.error(request, f"Error fetching emails: {str(e)}")

    return redirect('inbox')

@login_required
def email_settings_view(request):
    """View to configure email settings"""
    if request.method == 'POST':
        # Handle saving email settings
        # In a real application, you'd save these to user preferences
        messages.success(request, "Email settings updated successfully.")

    # For now, use system settings
    connection = setup_imap_connection(request.user)

    context = {
        'imap_server': connection.get('imap_server') if connection else '',
        'email_address': connection.get('email_address') if connection else '',
        'has_password': bool(connection and connection.get('password')),
    }

    return render(request, 'email/settings.html', context)
