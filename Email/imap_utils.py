import email
import imaplib
import datetime
from email.header import decode_header
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from .models import Email, EmailAttachment
import os
import tempfile
from django.core.files import File


def clean_body(body):
    """Clean and decode email body"""
    if body is None:
        return ""
    if isinstance(body, bytes):
        try:
            return body.decode("utf-8")
        except UnicodeDecodeError:
            try:
                return body.decode("latin-1")
            except UnicodeDecodeError:
                return "Unable to decode message body"
    return body


def clean_subject(subject):
    """Clean and decode email subject"""
    if subject is None:
        return "No Subject"
    if isinstance(subject, bytes):
        # decode the subject
        subject = decode_header(subject)[0][0]
        if isinstance(subject, bytes):
            try:
                subject = subject.decode("utf-8")
            except UnicodeDecodeError:
                subject = subject.decode("latin-1")
    return subject


def get_email_address(address_str):
    """Extract email address from a raw header"""
    if not address_str:
        return ""
    # If it's a bytes object, decode it
    if isinstance(address_str, bytes):
        try:
            address_str = address_str.decode("utf-8")
        except UnicodeDecodeError:
            address_str = address_str.decode("latin-1")

    # Check if address_str has '<email@example.com>' format
    if '<' in address_str and '>' in address_str:
        return address_str[address_str.find('<')+1:address_str.find('>')]
    return address_str


def fetch_emails(user, imap_server, email_address, password, limit=10, save_to_db=True):
    """
    Fetch emails from an IMAP server

    Args:
        user: Django user who owns these emails
        imap_server: IMAP server address (e.g., 'imap.gmail.com')
        email_address: Email address to fetch emails for
        password: Password for the email account
        limit: Maximum number of emails to fetch
        save_to_db: Whether to save fetched emails to the database

    Returns:
        List of fetched emails
    """
    fetched_emails = []

    try:
        # Create an IMAP4 instance over SSL
        imap = imaplib.IMAP4_SSL(imap_server)

        # Login to the account
        imap.login(email_address, password)

        # Select the inbox folder
        imap.select("INBOX")

        # Search for all emails in the inbox
        status, messages = imap.search(None, "ALL")
        if status != 'OK':
            return []

        # Get the list of email IDs
        email_ids = messages[0].split()

        # Limit the number of emails to fetch
        if limit and limit < len(email_ids):
            email_ids = email_ids[-limit:]

        # Process each email
        for email_id in reversed(email_ids):
            # Fetch the email
            status, msg_data = imap.fetch(email_id, "(RFC822)")
            if status != 'OK':
                continue

            # Parse the email content
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Extract email details
            subject = clean_subject(msg["Subject"])
            from_address = get_email_address(msg["From"])
            date_str = msg["Date"]

            # Get email body
            body = ""
            attachments = []

            if msg.is_multipart():
                # Handle multipart messages
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    # Extract the text parts
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = clean_body(part.get_payload(decode=True))
                        break
                    elif content_type == "text/html" and not body and "attachment" not in content_disposition:
                        body = clean_body(part.get_payload(decode=True))

                    # Handle attachments
                    if "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            # Save attachment to a temp file
                            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                                tmp.write(part.get_payload(decode=True))
                                tmp_path = tmp.name

                            attachments.append({
                                "filename": filename,
                                "path": tmp_path
                            })
            else:
                # Non-multipart emails
                body = clean_body(msg.get_payload(decode=True))

            # Create a timestamp
            try:
                # Try to parse the date
                from email.utils import parsedate_to_datetime
                date = parsedate_to_datetime(date_str)
            except (ValueError, TypeError):
                # Default to current time if date cannot be parsed
                date = timezone.now()

            email_data = {
                "subject": subject,
                "sender_email": from_address,
                "body": body,
                "date": date,
                "attachments": attachments
            }

            # Save to database if required
            if save_to_db:
                # Try to find recipient user by email
                try:
                    recipient = User.objects.get(email=email_address)
                except User.DoesNotExist:
                    recipient = None

                # Try to find sender in the system
                try:
                    sender = User.objects.get(email=from_address)
                except User.DoesNotExist:
                    sender = None

                # Create or get the email object
                email_obj, created = Email.objects.get_or_create(
                    sender_email=from_address,
                    recipient_email=email_address,
                    subject=subject,
                    defaults={
                        'sender': sender,
                        'recipient': recipient or user,
                        'body': body,
                        'created_at': date,
                        'sent_at': date,
                        'folder': 'inbox',
                        'is_read': False
                    }
                )

                if created:
                    # Save attachments
                    for attachment_data in attachments:
                        with open(attachment_data['path'], 'rb') as f:
                            attachment = EmailAttachment()
                            attachment.email = email_obj
                            attachment.filename = attachment_data['filename']
                            attachment.file.save(attachment_data['filename'], File(f))
                            attachment.save()

                        # Remove temp file
                        os.unlink(attachment_data['path'])

                    email_data['db_id'] = email_obj.id

            fetched_emails.append(email_data)

        # Logout when done
        imap.logout()

        return fetched_emails

    except Exception as e:
        print(f"Error fetching emails: {str(e)}")
        return []


def setup_imap_connection(user):
    """
    Set up IMAP connection for a user

    Returns connection details or None if settings are not configured
    """
    # Use the dedicated IMAP settings
    if hasattr(settings, 'IMAP_HOST') and hasattr(settings, 'IMAP_USER') and hasattr(settings, 'IMAP_PASSWORD'):
        return {
            'imap_server': settings.IMAP_HOST,
            'email_address': settings.IMAP_USER,
            'password': settings.IMAP_PASSWORD
        }
    # Fall back to email settings if IMAP not configured
    elif hasattr(settings, 'EMAIL_HOST_USER') and hasattr(settings, 'EMAIL_HOST_PASSWORD'):
        return {
            'imap_server': 'imap.gmail.com',  # Default to Gmail
            'email_address': settings.EMAIL_HOST_USER,
            'password': settings.EMAIL_HOST_PASSWORD
        }
    return None
