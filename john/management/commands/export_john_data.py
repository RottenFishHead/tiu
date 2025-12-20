from django.core.management.base import BaseCommand
from django.core.serializers import serialize
from john.models import Account, Bill, BillPayment, WorkEntry, MileageEntry, AccountWithdrawal
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Export all John app data to JSON file for PostgreSQL production import'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default=f'john_data_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            help='Output filename (default: john_data_export_YYYYMMDD_HHMMSS.json)',
        )

    def handle(self, *args, **options):
        output_file = options['output']
        
        self.stdout.write('Exporting John app data...')
        
        # Serialize all data
        data = {
            'accounts': json.loads(serialize('json', Account.objects.all())),
            'bills': json.loads(serialize('json', Bill.objects.all())),
            'bill_payments': json.loads(serialize('json', BillPayment.objects.all())),
            'account_withdrawals': json.loads(serialize('json', AccountWithdrawal.objects.all())),
            'work_entries': json.loads(serialize('json', WorkEntry.objects.all())),
            'mileage_entries': json.loads(serialize('json', MileageEntry.objects.all())),
        }
        
        # Write to file
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Print summary
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully exported data to: {output_file}'))
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'  - Accounts: {len(data["accounts"])}')
        self.stdout.write(f'  - Bills: {len(data["bills"])}')
        self.stdout.write(f'  - Bill Payments: {len(data["bill_payments"])}')
        self.stdout.write(f'  - Account Withdrawals: {len(data["account_withdrawals"])}')
        self.stdout.write(f'  - Work Entries: {len(data["work_entries"])}')
        self.stdout.write(f'  - Mileage Entries: {len(data["mileage_entries"])}')
        self.stdout.write(f'\nTo import in production, use: python manage.py loaddata {output_file}')
