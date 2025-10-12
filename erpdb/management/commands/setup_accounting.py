from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from erpdb.services import AccountingService


class Command(BaseCommand):
    help = 'Set up chart of accounts and sample journal entries for accounting system'

    def handle(self, *args, **options):
        self.stdout.write('Setting up accounting system...')
        
        # Create default chart of accounts
        self.stdout.write('Creating chart of accounts...')
        AccountingService.create_default_chart_of_accounts()
        self.stdout.write(self.style.SUCCESS('Chart of accounts created successfully!'))
        
        # Get or create a user for sample entries
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write('Created admin user with password: admin123')
        
        # Create sample journal entries
        self.stdout.write('Creating sample journal entries...')
        AccountingService.create_sample_journal_entries(user)
        self.stdout.write(self.style.SUCCESS('Sample journal entries created successfully!'))
        
        self.stdout.write(self.style.SUCCESS('Accounting system setup completed!'))
        self.stdout.write('You can now generate balance sheets with real data.')
