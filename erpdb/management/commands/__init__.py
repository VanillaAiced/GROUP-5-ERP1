# Commands
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Make user a superuser'

    def handle(self, *args, **options):
        try:
            user = User.objects.get(username='yuzuruw')
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully made {user.username} a superuser!'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User yuzuruw not found'))

