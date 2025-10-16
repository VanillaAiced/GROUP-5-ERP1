from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix inconsistent migration history by marking missing migrations as applied'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check which migrations are currently applied
            cursor.execute(
                "SELECT app, name FROM django_migrations WHERE app = 'erpdb' ORDER BY id"
            )
            applied = cursor.fetchall()

            self.stdout.write("Currently applied migrations:")
            for app, name in applied:
                self.stdout.write(f"  [{app}] {name}")

            # Migrations that need to be marked as applied
            missing_migrations = [
                ('erpdb', '0004_alter_purchaseorderitem_unit_price'),
                ('erpdb', '0004_alter_category_options_alter_warehouse_options_and_more'),
            ]

            # Check which ones are actually missing
            applied_names = [name for app, name in applied]

            for app, migration_name in missing_migrations:
                if migration_name not in applied_names:
                    self.stdout.write(
                        self.style.WARNING(f"Marking {migration_name} as applied...")
                    )
                    cursor.execute(
                        "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW())",
                        [app, migration_name]
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"{migration_name} already applied")
                    )

            self.stdout.write(
                self.style.SUCCESS('Migration history fixed! You can now run: python manage.py migrate')
            )

