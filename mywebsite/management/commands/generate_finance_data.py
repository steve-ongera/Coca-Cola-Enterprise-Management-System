from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from mywebsite.models import Account, Transaction, TransactionEntry, Budget, Payment, TaxRecord, Department
from django.utils import timezone
from random import choice, randint, uniform
from decimal import Decimal
import datetime
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate sample finance data for Almasi Bottlers ERP system'

    def handle(self, *args, **kwargs):
        # Create Departments
        departments = ['Finance', 'Human Resources', 'Production', 'Sales']
        department_objs = []
        for dept_name in departments:
            dept, _ = Department.objects.get_or_create(name=dept_name)
            department_objs.append(dept)

        # Create Users
        user, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@almasi.com', 'password': 'cp7kvt'})
        approver, _ = User.objects.get_or_create(username='approver', defaults={'email': 'approver@almasi.com', 'password': 'cp7kvt'})

        # Create Accounts
        account_types = ['asset', 'liability', 'equity', 'revenue', 'expense']
        accounts = []
        for i in range(10):
            acc = Account.objects.create(
                account_number=f"ACC{i+1000}",
                name=f"Account {i+1}",
                account_type=choice(account_types),
                balance=Decimal(uniform(10000, 500000)).quantize(Decimal("0.01")),
                is_active=True
            )
            accounts.append(acc)

        # Create Transactions and Entries
        for i in range(5):
            txn = Transaction.objects.create(
                transaction_date=timezone.now().date() - datetime.timedelta(days=randint(0, 30)),
                description=f"Transaction {i+1} description",
                reference_number=f"TREF{i+100}",
                status='posted',
                created_by=user,
                approved_by=approver
            )

            acc1, acc2 = choice(accounts), choice(accounts)
            amt = Decimal(uniform(1000, 50000)).quantize(Decimal("0.01"))
            TransactionEntry.objects.create(transaction=txn, account=acc1, amount=amt, entry_type='debit')
            TransactionEntry.objects.create(transaction=txn, account=acc2, amount=amt, entry_type='credit')

        # Create Budgets
        for dept in department_objs:
            for acc in accounts:
                Budget.objects.get_or_create(
                    fiscal_year="2025",
                    department=dept,
                    account=acc,
                    amount=Decimal(uniform(10000, 200000)).quantize(Decimal("0.01")),
                    period=choice(['monthly', 'quarterly', 'yearly']),
                    approved_by=approver
                )

        # Create Payments
        for i in range(3):
            payment = Payment.objects.create(
                payment_number=f"PAY{i+200}",
                payment_date=timezone.now().date(),
                amount=Decimal(uniform(2000, 10000)).quantize(Decimal("0.01")),
                payment_method=choice(['cash', 'check', 'bank_transfer', 'credit_card']),
                content_type=ContentType.objects.get_for_model(Transaction),
                object_id=Transaction.objects.order_by('?').first().id,
                received_by=user,
                notes="Sample payment"
            )

        # Create Tax Records
        for i in range(3):
            TaxRecord.objects.create(
                tax_type=choice(['VAT', 'PAYE', 'Excise']),
                period_start=timezone.now().date() - datetime.timedelta(days=60),
                period_end=timezone.now().date() - datetime.timedelta(days=30),
                amount=Decimal(uniform(5000, 30000)).quantize(Decimal("0.01")),
                filing_date=timezone.now().date() - datetime.timedelta(days=15),
                status=choice(['pending', 'filed', 'paid']),
                documents={"filename": f"tax_document_{i+1}.pdf"}
            )

        self.stdout.write(self.style.SUCCESS("✔ Successfully generated sample finance data."))
