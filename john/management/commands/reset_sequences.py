from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Reset PostgreSQL sequences for john app tables to prevent duplicate key errors'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # List of tables in the john app that have auto-incrementing primary keys
            tables = [
                'john_account',
                'john_bill',
                'john_billpayment',
                'john_accountwithdrawal',
                'john_workentry',
                'john_mileageentry',
            ]
            
            for table in tables:
                # Get the current maximum ID
                cursor.execute(f"SELECT MAX(id) FROM {table}")
                max_id = cursor.fetchone()[0]
                
                if max_id is not None:
                    # Reset the sequence to max_id + 1
                    sequence_name = f"{table}_id_seq"
                    cursor.execute(f"SELECT setval('{sequence_name}', {max_id}, true)")
                    self.stdout.write(
                        self.style.SUCCESS(f'Reset sequence for {table} to {max_id}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'No records found in {table}, skipping')
                    )
        
        self.stdout.write(
            self.style.SUCCESS('All sequences have been reset successfully!')
        )
