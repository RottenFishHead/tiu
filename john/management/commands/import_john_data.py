from django.core.management.base import BaseCommand
from john.models import Account, Bill, BillPayment, WorkEntry, MileageEntry, AccountWithdrawal
import json
from decimal import Decimal
from datetime import datetime, date, time


class Command(BaseCommand):
    help = 'Import John app data from JSON export file'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Path to the JSON file to import',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing',
        )

    def handle(self, *args, **options):
        json_file = options['json_file']
        clear_data = options['clear']
        
        self.stdout.write(f'Loading data from {json_file}...')
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            MileageEntry.objects.all().delete()
            WorkEntry.objects.all().delete()
            AccountWithdrawal.objects.all().delete()
            BillPayment.objects.all().delete()
            Bill.objects.all().delete()
            Account.objects.all().delete()
        
        # Import Accounts
        account_map = {}
        for item in data.get('accounts', []):
            fields = item['fields']
            account = Account.objects.create(
                id=item['pk'],
                name=fields['name'],
                institution=fields.get('institution', ''),
                number_last4=fields.get('number_last4', ''),
                is_active=fields.get('is_active', True)
            )
            account_map[item['pk']] = account
        self.stdout.write(f'Imported {len(account_map)} accounts')
        
        # Import Bills
        bill_map = {}
        for item in data.get('bills', []):
            fields = item['fields']
            bill = Bill.objects.create(
                id=item['pk'],
                name=fields['name'],
                amount=Decimal(str(fields['amount'])),
                due_day=fields['due_day'],
                is_auto_pay=fields.get('is_auto_pay', False),
                account_id=fields['account'],
                notes=fields.get('notes', ''),
                active=fields.get('active', True),
                created_at=fields.get('created_at'),
                updated_at=fields.get('updated_at')
            )
            bill_map[item['pk']] = bill
        self.stdout.write(f'Imported {len(bill_map)} bills')
        
        # Import Bill Payments
        payment_count = 0
        for item in data.get('bill_payments', []):
            fields = item['fields']
            BillPayment.objects.create(
                id=item['pk'],
                bill_id=fields['bill'],
                account_id=fields['account'],
                amount=Decimal(str(fields['amount'])),
                date_paid=fields['date_paid'],
                receipt_image=fields.get('receipt_image', ''),
                notes=fields.get('notes', ''),
                created_at=fields.get('created_at'),
                updated_at=fields.get('updated_at')
            )
            payment_count += 1
        self.stdout.write(f'Imported {payment_count} bill payments')
        
        # Import Account Withdrawals
        withdrawal_count = 0
        for item in data.get('account_withdrawals', []):
            fields = item['fields']
            AccountWithdrawal.objects.create(
                id=item['pk'],
                account_id=fields['account'],
                bill_id=fields.get('bill'),
                amount=Decimal(str(fields['amount'])),
                date=fields['date'],
                method=fields.get('method', 'ACH'),
                memo=fields.get('memo', ''),
                created_at=fields.get('created_at'),
                updated_at=fields.get('updated_at')
            )
            withdrawal_count += 1
        self.stdout.write(f'Imported {withdrawal_count} account withdrawals')
        
        # Import Work Entries
        work_count = 0
        for item in data.get('work_entries', []):
            fields = item['fields']
            
            # Parse time fields
            start_time = None
            end_time = None
            if fields.get('start_time'):
                try:
                    start_time = datetime.strptime(fields['start_time'], '%H:%M:%S').time()
                except:
                    pass
            if fields.get('end_time'):
                try:
                    end_time = datetime.strptime(fields['end_time'], '%H:%M:%S').time()
                except:
                    pass
            
            WorkEntry.objects.create(
                id=item['pk'],
                date=fields['date'],
                description=fields.get('description', ''),
                start_time=start_time,
                end_time=end_time,
                hours=Decimal(str(fields['hours'])) if fields.get('hours') else None,
                hourly_rate=Decimal(str(fields['hourly_rate'])),
                amount=Decimal(str(fields['amount'])) if fields.get('amount') else None,
                notes=fields.get('notes', ''),
                created_at=fields.get('created_at'),
                updated_at=fields.get('updated_at')
            )
            work_count += 1
        self.stdout.write(f'Imported {work_count} work entries')
        
        # Import Mileage Entries
        mileage_count = 0
        for item in data.get('mileage_entries', []):
            fields = item['fields']
            MileageEntry.objects.create(
                id=item['pk'],
                date=fields['date'],
                description=fields.get('description', ''),
                starting_mileage=Decimal(str(fields['starting_mileage'])) if fields.get('starting_mileage') else None,
                ending_mileage=Decimal(str(fields['ending_mileage'])) if fields.get('ending_mileage') else None,
                miles=Decimal(str(fields['miles'])) if fields.get('miles') else None,
                rate_per_mile=Decimal(str(fields['rate_per_mile'])),
                amount=Decimal(str(fields['amount'])) if fields.get('amount') else None,
                notes=fields.get('notes', ''),
                created_at=fields.get('created_at'),
                updated_at=fields.get('updated_at')
            )
            mileage_count += 1
        self.stdout.write(f'Imported {mileage_count} mileage entries')
        
        self.stdout.write(self.style.SUCCESS('\nImport completed successfully!'))
