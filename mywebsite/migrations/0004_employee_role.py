# Generated by Django 5.1.2 on 2025-04-09 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mywebsite', '0003_employee_address_employee_bank_account_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='role',
            field=models.CharField(blank=True, choices=[('employee', 'Employee'), ('manager', 'Manager'), ('admin', 'Admin')], max_length=100, null=True),
        ),
    ]
