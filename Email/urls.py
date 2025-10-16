from django.urls import path
from Email.views import (
    inbox_view,
    email_detail_view,
    compose_email_view,
    delete_email_view,
    star_email_view,
    mark_as_read_view,
    mark_as_unread_view,
    fetch_external_emails_view,
    email_settings_view
)

urlpatterns = [
    path('inbox/', inbox_view, name='inbox'),
    path('compose/', compose_email_view, name='compose_email'),
    path('email/<int:email_id>/', email_detail_view, name='email_detail'),
    path('email/<int:email_id>/delete/', delete_email_view, name='delete_email'),
    path('email/<int:email_id>/star/', star_email_view, name='star_email'),
    path('email/<int:email_id>/mark-read/', mark_as_read_view, name='mark_as_read'),
    path('email/<int:email_id>/mark-unread/', mark_as_unread_view, name='mark_as_unread'),
    path('fetch-external/', fetch_external_emails_view, name='fetch_external_emails'),
    path('settings/', email_settings_view, name='email_settings'),
]